from services.models import SCurrentHDRequest


def show_request_info(request: SCurrentHDRequest, is_admin: bool = False) -> str:
    return f'''
<b>Запрос в техподдержку №{request.id}</b>
{'<b>Идентификатор пользователя:</b> {}'.format(request.user_id) if is_admin else ''}
<b>Тип запроса:</b> 
{request.name}
    
<b>Отправлен:</b> {request.created_at.strftime("%d.%m.%Y %H:%M:%S")}
<b>Выполнен:</b> {request.done_at.strftime("%d.%m.%Y %H:%M:%S") if request.done_at else ''}
    
<b>Текст запроса:</b>
<i>{request.request_text}</i>
    
<b>Текст решения:</b>
<i>{request.solution_text or ''}</i>'''
