alias w := watchexec

_default:
    just --list

watchexec:
    watchexec -c -e py python main.py

