const sqlite3 = require('sqlite3');

/**
 * Wraps sqlite3 with a Promise-based API. The connection is opened on first use
 * and exposed via three helpers: get(sql, params), all(sql, params), run(sql, params).
 * run resolves to { lastID, changes }, matching the legacy `this`-binding contract.
 */
function createDatabase(filename = ':memory:') {
    const raw = new sqlite3.Database(filename);

    function get(sql, params = []) {
        return new Promise((resolve, reject) => {
            raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    function all(sql, params = []) {
        return new Promise((resolve, reject) => {
            raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    function run(sql, params = []) {
        return new Promise((resolve, reject) => {
            raw.run(sql, params, function (err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    function exec(sql) {
        return new Promise((resolve, reject) => {
            raw.exec(sql, (err) => (err ? reject(err) : resolve()));
        });
    }

    function close() {
        return new Promise((resolve, reject) => {
            raw.close((err) => (err ? reject(err) : resolve()));
        });
    }

    return { get, all, run, exec, close };
}

async function initializeSchema(db) {
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, pass TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id), course_id INTEGER NOT NULL REFERENCES courses(id));
        CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, enrollment_id INTEGER NOT NULL REFERENCES enrollments(id), amount REAL NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);
    `);
}

async function seedIfEmpty(db, { hashPassword }) {
    const count = await db.get('SELECT COUNT(*) AS n FROM users');
    if (count && count.n > 0) return;

    const hash = await hashPassword('123');
    await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', hash]);
    await db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
    await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
}

module.exports = { createDatabase, initializeSchema, seedIfEmpty };
