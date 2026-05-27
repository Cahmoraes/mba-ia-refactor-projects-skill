const { AppError } = require('../middlewares/errorHandler');

function buildUserController({ users }) {
    async function deleteUser(userId) {
        const id = parseInt(userId, 10);
        if (Number.isNaN(id)) throw new AppError('userId inválido', 400);
        const ok = await users.deleteCascade(id);
        if (!ok) throw new AppError('Usuário não encontrado', 404);
    }
    return { deleteUser };
}

module.exports = { buildUserController };
