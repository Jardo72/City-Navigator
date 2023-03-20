from fastapi import HTTPException, status


def means_of_transport_not_found_exception(uuid: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Means of transport with the UUID '{uuid}' not found."
    )


def station_not_found_exception(uuid: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Station with the UUID '{uuid}' not found."
    )


def line_not_found_exception(uuid: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Line with the UUID '{uuid}' not found."
    )
