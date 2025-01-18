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
