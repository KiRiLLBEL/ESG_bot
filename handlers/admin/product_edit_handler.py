from aiogram import Router, F, Bot
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import callback_map_admin
from services.database import add_product
from states.admin_states import Admin

router = Router()

@router.message(StateFilter(Admin.product_name), F.content_type == ContentType.TEXT,  F.text.len() < 64)
async def add_name_product(message: Message,  state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.product_score)
    msg = await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите стоимость продукта')
    await state.set_data({"name": message.text, "msg": msg.message_id})
    await message.delete()

@router.message(StateFilter(Admin.product_score), F.text.isdigit())
async def add_name_product(message: Message,  state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg = data.get('msg')
    await state.set_state(Admin.product_image)
    msg = await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Введите ссылку на изображение товара')
    await state.set_data({"name": data['name'], "msg": msg.message_id, 'price': int(message.text)})
    await message.delete()


@router.message(StateFilter(Admin.product_image), F.content_type == ContentType.TEXT)
async def add_name_product(message: Message,  state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    msg = data.get('msg')
    await add_product(session, data['name'], data['price'], message.text)
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg, text='Товар успешно создан', reply_markup=callback_map_admin['menu'])
    await state.set_state(Admin.join)
    await message.delete()