async def validade_unique_email(list_users, new_email):
    for user in list_users:
        if user["email"] == new_email:
            return False
    return True
