const { AppError } = require('../middlewares/errorHandler');
const logger = require('../utils/logger');

function maskCard(card) {
    const s = String(card);
    return s.length >= 4 ? `****${s.slice(-4)}` : '****';
}

function mockChargeCard(card) {
    return String(card).startsWith('4') ? 'PAID' : 'DENIED';
}

function buildCheckoutController({ users, courses, enrollments, payments, auditLogs, hashPassword }) {
    async function processCheckout(payload) {
        const course = await courses.findActiveById(payload.courseId);
        if (!course) throw new AppError('Curso não encontrado', 404);

        const status = mockChargeCard(payload.card);
        logger.info('checkout.attempt', { courseId: course.id, card: maskCard(payload.card) });
        if (status === 'DENIED') throw new AppError('Pagamento recusado', 400);

        let user = await users.findByEmail(payload.email);
        if (!user) {
            const passwordHash = await hashPassword(payload.password);
            const userId = await users.create({
                name: payload.name,
                email: payload.email,
                passwordHash,
            });
            user = { id: userId, name: payload.name, email: payload.email };
        }

        const enrollmentId = await enrollments.create({ userId: user.id, courseId: course.id });
        await payments.create({ enrollmentId, amount: course.price, status });
        await auditLogs.record(`Checkout curso ${course.id} por ${user.id}`);

        logger.info('checkout.success', { userId: user.id, enrollmentId });
        return { enrollmentId };
    }

    return { processCheckout };
}

module.exports = { buildCheckoutController };
