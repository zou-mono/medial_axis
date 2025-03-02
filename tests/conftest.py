import pytest
from shapely import geometry


@pytest.fixture(params=[True, False])
def simple_polygon(create_polygon, request):
    points = [
        (4.8, 7),
        (6.5, 6.3), (6.8, 5.6), (9, 5),
        (8.8, 4), (8, 3.2), (8.4, 2.5),
        (5, 1), (3.85, 1.96), (3.85, 3),
        (5.5, 3), (5.5, 4), (4.8, 4.7),
        (3.5, 4.2),
        (2.8, 4.9), (3.2, 5.9), (4.8, 7)
    ]

    # points = [
    #     (3.5, 4.2),
    #     (2.8, 4.9), (3.2, 5.9), (4.8, 7),
    #     (6.5, 6.3), (6.8, 5.6), (9, 5),
    #     (8.8, 4), (8, 3.2), (8.4, 2.5),
    #     (5, 1), (3.85, 1.96), (3.85, 3),
    #     (5.5, 3), (5.5, 4), (4.8, 4.7),
    #     (3.5, 4.2)
    # ]

    # if not request.param:
    #     points.reverse()

    return create_polygon(exterior=points), request.param


@pytest.fixture(params=[False])
def simple_polygon2(create_polygon, request):
    points = [
        (13.52883346333501, 68.31918372289175),
        (14.014665134273772, 69.0622203960922),
        (14.700545140304964, 68.09055705421468),
        (14.786280141058862, 55.201728607545206),
        (14.300448470120102, 53.60134192680576),
        (13.443098462581112, 55.11599360679131),
        (13.52883346333501, 68.31918372289175)
    ]

    # if not request.param:
    #     points.reverse()

    return create_polygon(exterior=points), request.param


@pytest.fixture(params=[True, False])
def five_pointed_star(create_polygon, request):
    # points = [
    #     (1.0, 0.0),
    #     (0.3249, 0.1236),
    #     (0.3090, 0.9511),
    #     (-0.1, 0.3804),
    #     (-0.8090, 0.5878),
    #     (-0.4, 0),
    #     (-0.8090, -0.5878),
    #     (-0.1, -0.3804),
    #     (0.3090, -0.9511),
    #     (0.3249, -0.1236),
    #     (1.0, 0.0)
    # ]
    points = [
        (1.0000, 0.0000),
        (0.3090, 0.2245),
        (0.3090, 0.9511),
        (-0.1180, 0.3633),
        (-0.8090, 0.5878),
        (-0.3820, 0.0000),
        (-0.8090, -0.5878),
        (-0.1180, -0.3633),
        (0.3090, -0.9511),
        (0.3090, -0.2245),
        (1, 0)
    ]
    if not request.param:
        points.reverse()

    return create_polygon(exterior=points), request.param


@pytest.fixture
def create_polygon():
    def _create_polygon(exterior, holes=None):
        return geometry.Polygon(exterior, holes)

    return _create_polygon


