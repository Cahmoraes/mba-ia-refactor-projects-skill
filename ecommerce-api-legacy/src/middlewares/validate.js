const { AppError } = require('./errorHandler');

const EMAIL_REGEX = /^[a-zA-Z0-9+_.\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
const CARD_REGEX = /^[0-9]{13,19}$/;

function validateCheckoutPayload(body) {
    const name = body.name ?? body.usr;
    const email = body.email ?? body.eml;
    const password = body.password ?? body.pwd;
    const courseId = body.courseId ?? body.c_id;
    const card = body.card;

    if (!name || typeof name !== 'string') throw new AppError('name é obrigatório', 400);
    if (!email || !EMAIL_REGEX.test(email)) throw new AppError('email inválido', 400);
    if (password && password.length < 4) throw new AppError('password muito curto', 400);
    if (!courseId || Number.isNaN(parseInt(courseId, 10))) throw new AppError('courseId inválido', 400);
    if (!card || !CARD_REGEX.test(String(card))) throw new AppError('card inválido', 400);

    return {
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password: password || '123456',
        courseId: parseInt(courseId, 10),
        card: String(card),
    };
}

module.exports = { validateCheckoutPayload };
