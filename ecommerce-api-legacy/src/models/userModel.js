function userModel(db) {
    async function findByEmail(email) {
        return db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
    }

    async function findByEmailWithPassword(email) {
        return db.get('SELECT id, name, email, pass FROM users WHERE email = ?', [email]);
    }

    async function create({ name, email, passwordHash }) {
        const { lastID } = await db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash],
        );
        return lastID;
    }

    async function deleteCascade(userId) {
        // Remove dependent data first to avoid orphans.
        const enrollments = await db.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
        const enrollmentIds = enrollments.map((e) => e.id);
        if (enrollmentIds.length > 0) {
            const placeholders = enrollmentIds.map(() => '?').join(',');
            await db.run(`DELETE FROM payments WHERE enrollment_id IN (${placeholders})`, enrollmentIds);
            await db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
        }
        const { changes } = await db.run('DELETE FROM users WHERE id = ?', [userId]);
        return changes > 0;
    }

    return { findByEmail, findByEmailWithPassword, create, deleteCascade };
}

module.exports = { userModel };
