const { Router } = require('express');

function buildReportRoutes({ reportController }) {
    const router = Router();

    router.get('/api/admin/financial-report', async (req, res, next) => {
        try {
            const report = await reportController.buildFinancialReport();
            res.json(report);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = { buildReportRoutes };
