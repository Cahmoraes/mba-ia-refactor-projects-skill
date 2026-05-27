const { Router } = require('express');

function buildUserRoutes({ userController }) {
    const router = Router();

    router.delete('/api/users/:id', async (req, res, next) => {
        try {
            await userController.deleteUser(req.params.id);
            res.json({ msg: 'Usuário deletado com matrículas e pagamentos relacionados' });
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = { buildUserRoutes };
