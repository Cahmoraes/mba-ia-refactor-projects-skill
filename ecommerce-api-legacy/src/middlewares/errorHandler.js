const logger = require('../utils/logger');

class AppError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.status = status;
        this.expose = true;
    }
}

function errorHandler(err, req, res, _next) {
    if (err instanceof AppError) {
        return res.status(err.status).json({ error: err.message });
    }
    logger.error('unhandled.exception', { path: req.path, message: err.message });
    res.status(500).json({ error: 'Internal Server Error' });
}

module.exports = { AppError, errorHandler };
