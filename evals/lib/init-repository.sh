#!/usr/bin/env bash

init_fixture_repository() {
  local directory="$1"
  local remote="$2"

  git -C "$directory" init -q
  git -C "$directory" config user.name "QaaS Eval"
  git -C "$directory" config user.email "qaas-eval@example.invalid"
  git -C "$directory" remote add origin "$remote"
  git -C "$directory" add .
  git -C "$directory" commit -qm "Create eval fixture"
}
