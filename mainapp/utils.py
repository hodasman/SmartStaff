def decline_devices(count: int) -> str:
    """
    Правильное склонение слова 'устройство' по количеству.

    Args:
        count: Количество устройств

    Returns:
        Правильная форма слова
    """
    if count % 10 == 1 and count % 100 != 11:
        return "Устройство"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "Устройства"
    else:
        return "Устройств"


def decline_device_types(count: int) -> str:
    """
    Правильное склонение словосочетания 'тип устройства' по количеству.

    Args:
        count: Количество типов устройств

    Returns:
        Правильная форма словосочетания
    """
    if count % 10 == 1 and count % 100 != 11:
        return "тип устройства"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "типа устройств"
    else:
        return "типов устройств"