def standard_return(data, success: bool, err):
    if success:
        return {
            "data": data,
            "success": True
        }
    return {
        "data": err,
        "success": False
    }
