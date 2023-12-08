HELP = {
    'default': 'Данный раздел находится в разработке.',
    'base': '''
    Вы находитесь в разделе меню <b>Помощь</b>.
    Здесь разобраны все основные последовательности действий при работе с ботом.
    
    Для возврата к начальному меню выберите команду /start .
    Для отмены любого действия и возврата к начальному меню можно использовать команду /cancel .
    
    Для дальнейшей работы в данном разделе, выберите по какому разделу вам нужна помощь или пояснения.
    ''',
    'auth': '''
    
    Авторизация необходима для начала работы с ботом. 
    <b>Без прохождения этого этапа вам будет недоступна работа с заказами еды.</b>
    
    <b><u>Этапы прохождения авторизации:</u></b>
    1) Необходимо в Меню выбрать команду /start .
    2) Нажать на появившуюся внизу кнопку <b><i>Авторизоваться</i></b>.
    3) Принять запрос на предоставление контактных данных.
    Этот этап важен, так как именно по нему будет определено являетесь ли вы заказчиком столовой или нет.
    Также надо обратить внимание на то, что ваш номер телефона, с которого вы пытаетесь пройти этот этап, 
    должен совпадать с номером телефона, указанным вами в отделе кадров в качестве основного контактного номера. Если это не так, то обратитесь в отдел кадров для изменения информации по вашему основному контактному номеру.
    4) После проверки соответствия номеров телефонов, необходимо выбрать место доставки еды, определенное столовой.
    Если у вас есть разрешения для заказа еды сразу в нескольких столовых, то сначала необходимо выбрать из них одну.
    
    Когда вы справитесь с этапом №4 система допустит вас до работы с заказами.
    Место доставки можно изменить в любое время после авторизации.
    Для этого необходимо нажать кнопку <b><i>Изменить место доставки</i></b>.
    ''',

    'order': '''
    
    Работа с заказами является основной функцией этого бота.
    Разобьем эту работу на 2 составляющие и поясним работу по каждой в отдельности.
    
    <b><u>1. Новый заказ</u></b>
        1) Для регистрации нового заказа необходимо нажать на кнопку <b><i>Сделать новый заказ</i></b>.
        2) Выбрать из списка на какое меню вы хотите сделать заказ.
        Если вы выбрали не то меню, нажмите на кнопку <b><i>Отменить</i></b>.
        3) С помощью кнопок <b><i>-1</i></b> и <b><i>+1</i></b> настроить необходимое количество позиции данного меню.
        4) Нажать на кнопку <b><i>Выбрать</i></b> под описанием позиции, которую хотите заказать.
        5) Если вы добавили не ту позицию или не то количество, нажмите на кнопку <b><i>Отменить</i></b>.
        6) После того, как вы выберете все позиции меню, которые хотите заказать, нажмите на кнопку <b><i>Подтвердить</i></b>.
        7) Проверьте свой заказ, представленный в контрольном сообщении и нажмите на кнопку <b><i>Отправить</i></b>.
        Вам придет уведомление, что заказ отправлен успешно.
        8) Если вы увидели, что вы где-то ошиблись с формированием заказа нажмите кнопку <b><i>Отменить</i></b>.
        
    <b><u>2. Отмена заказа</u></b>
        1) Для отмены уже отправленного заказа нажмите на кнопку <b><i>Отменить заказ</i></b>.
        2) Из списка ваших заказов, доступных для отмены, выберите нужный и нажмите кнопку <b><i>Отменить заказ</i></b>. После отмены заказа вы получите уведомление об успешности данной операции.
        3) Чтобы вернуться в начальное меню нажмите на кнопку <b><i>Вернуться в главное меню</i></b>.
    '''
}


def help_info(callback_data: str) -> str:
    chapter, _ = callback_data.split('_')
    return HELP.get(chapter, HELP.get('default'))
