alias w := watchexec
alias t := test

_default:
    just --list

watchexec:
    watchexec -c -e py python main.py

test:
    watchexec -c -e py pytest --sw

pdb:
    pytest --sw --pdb

