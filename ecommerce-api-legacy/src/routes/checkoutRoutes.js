const { Router } = require('express');

const { validateCheckoutPayload } = require('../middlewares/validate');

function buildCheckoutRoutes({ checkoutController }) {
    const router = Router();

    router.post('/api/checkout', async (req, res, next) => {
        try {
            const payload = validateCheckoutPayload(req.body || {});
            const result = await checkoutController.processCheckout(payload);
            res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = { buildCheckoutRoutes };
