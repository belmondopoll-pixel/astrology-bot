def split_message(text: str, max_length: int = 4096) -> list[str]:
    """
    Разбивает текст на части, не превышающие max_length.
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        
        # Ищем место для разбиения (по абзацу или предложению)
        split_index = text.rfind('\n\n', 0, max_length)
        if split_index == -1:
            split_index = text.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = text.rfind('. ', 0, max_length)
        if split_index == -1:
            split_index = text.rfind(' ', 0, max_length)
        
        # Если не нашли подходящее место, просто обрезаем
        if split_index == -1:
            split_index = max_length
        
        parts.append(text[:split_index].strip())
        text = text[split_index:].strip()
    
    return parts