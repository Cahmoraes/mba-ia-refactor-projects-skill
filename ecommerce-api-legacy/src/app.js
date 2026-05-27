/**
 * Composition root — wires Express, config, DB, models, controllers, routes and middlewares.
 */
const express = require('express');

const config = require('./config');
const { createDatabase, initializeSchema, seedIfEmpty } = require('./infrastructure/database');
const { hashPassword } = require('./utils/crypto');
const { errorHandler } = require('./middlewares/errorHandler');
const logger = require('./utils/logger');

const { userModel } = require('./models/userModel');
const { courseModel } = require('./models/courseModel');
const { enrollmentModel } = require('./models/enrollmentModel');
const { paymentModel } = require('./models/paymentModel');
const { auditLogModel } = require('./models/auditLogModel');

const { buildCheckoutController } = require('./controllers/checkoutController');
const { buildReportController } = require('./controllers/reportController');
const { buildUserController } = require('./controllers/userController');

const { buildCheckoutRoutes } = require('./routes/checkoutRoutes');
const { buildReportRoutes } = require('./routes/reportRoutes');
const { buildUserRoutes } = require('./routes/userRoutes');

async function bootstrap() {
    const db = createDatabase(':memory:');
    await initializeSchema(db);
    await seedIfEmpty(db, { hashPassword });

    const users = userModel(db);
    const courses = courseModel(db);
    const enrollments = enrollmentModel(db);
    const payments = paymentModel(db);
    const auditLogs = auditLogModel(db);

    const checkoutController = buildCheckoutController({
        users,
        courses,
        enrollments,
        payments,
        auditLogs,
        hashPassword,
    });
    const reportController = buildReportController({ db });
    const userController = buildUserController({ users });

    const app = express();
    app.use(express.json());

    app.get('/health', (_req, res) => res.json({ status: 'ok' }));
    app.use(buildCheckoutRoutes({ checkoutController }));
    app.use(buildReportRoutes({ reportController }));
    app.use(buildUserRoutes({ userController }));

    app.use(errorHandler);

    app.listen(config.port, () => {
        logger.info('server.start', { port: config.port });
    });
}

bootstrap().catch((err) => {
    logger.error('bootstrap.failed', { message: err.message });
    process.exit(1);
});
