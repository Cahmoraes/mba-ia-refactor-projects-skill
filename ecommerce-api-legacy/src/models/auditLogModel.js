function auditLogModel(db) {
    async function record(action) {
        await db.run('INSERT INTO audit_logs (action) VALUES (?)', [action]);
    }
    return { record };
}

module.exports = { auditLogModel };
