const config = require('../config');

const LEVELS = { error: 0, warn: 1, info: 2, debug: 3 };
const currentLevel = LEVELS[config.logLevel] ?? LEVELS.info;

function log(level, event, payload = {}) {
    if (LEVELS[level] > currentLevel) return;
    const entry = { ts: new Date().toISOString(), level, event, ...payload };
    const line = JSON.stringify(entry);
    if (level === 'error') console.error(line);
    else console.log(line);
}

module.exports = {
    info: (event, payload) => log('info', event, payload),
    warn: (event, payload) => log('warn', event, payload),
    error: (event, payload) => log('error', event, payload),
    debug: (event, payload) => log('debug', event, payload),
};
