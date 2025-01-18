import pytest
from psirc.user_manager import UserManager, NickAlreadyInUse


def test_constructor():
    manager = UserManager()
    assert len(manager.list_users()) == 0


def test_add_local_user():
    manager = UserManager()
    dummy_socket = "socket"
    manager.add_local("nickname", dummy_socket)
    user = manager.get_user("nickname")
    assert user.is_local()
    assert user.hop_count == 0
    assert user.nick == "nickname"
    assert user.get_route() == "socket"


def test_add_external():
    manager = UserManager()
    manager.add_external("nickname", 1, "server_nickname")
    user = manager.get_user("nickname")
    assert not user.is_local()
    assert user.hop_count == 1
    assert user.get_route() == "server_nickname"


def test_nickname_collisions():
    manager = UserManager()
    manager.add_external("nickname", 1, "server")
    with pytest.raises(NickAlreadyInUse):
        manager.add_local("nickname", "socket")


def test_external_hop_count_non_positive():
    manager = UserManager()
    with pytest.raises(ValueError):
        manager.add_external("nickname", 0, "server")


def test_remove_from_server():
    manager = UserManager()
    manager.add_local("nickname", "socket")
    manager.add_external("nickname1", 1, "server_nickname")
    manager.add_external("nickname2", 1, "server_nickname")
    manager.add_external("nickname3", 1, "other_server")
    disconnected = manager.remove_from_server("server_nickname")
    assert len(disconnected) == 2
    assert any([user.nick == "nickname1" for user in disconnected])
    assert any([user.nick == "nickname2" for user in disconnected])
    assert len(manager.list_users()) == 2
    assert any([user == "nickname" for user in manager.list_users()])
    assert any([user == "nickname3" for user in manager.list_users()])
