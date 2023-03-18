from fastapi import HTTPException, status


def station_not_found_exception(name: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Station with the name '{name}' not found."
    )


def line_not_found_exception(label: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Line with the label '{label}' not found."
    )
