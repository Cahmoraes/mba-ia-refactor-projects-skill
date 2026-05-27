function courseModel(db) {
    async function findActiveById(id) {
        return db.get('SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [id]);
    }

    async function listAll() {
        return db.all('SELECT id, title, price, active FROM courses');
    }

    return { findActiveById, listAll };
}

module.exports = { courseModel };
