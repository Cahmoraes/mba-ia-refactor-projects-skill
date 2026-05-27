function paymentModel(db) {
    async function create({ enrollmentId, amount, status }) {
        const { lastID } = await db.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status],
        );
        return lastID;
    }

    return { create };
}

module.exports = { paymentModel };
