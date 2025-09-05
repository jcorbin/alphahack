# 2025-09-06

```ex
'<,'>norm ^f dt f🧩2f dt 0f P
```

Details spoilers:

# Dev

## WIP

- space search eof no longer works
  ```
  search 722964 [ 1400 cap:1400 prune:88 dead:2 reject:1 ]> ! <__main__.Search object at 0x7e043b5a4190> -!> Search.__call__.<locals>.<lambda>
  ```

- store fin
  - doesn't commit
  - should auto report
  - ... from review, but seems fine under cont

## TODO

- both hurdle and dontwordle lack puzzle id in report notes

- semantic does not auto report before exit
  - auto seems to just `<STOP>`, but not trace to confirm yet
  - rerun insta stores with trace:
    ```
    ! __call__ -> load_log
    ! load_log -> set_log_file
    ! set_log_file -*> load
    ! __call__ -> handle
    ! handle -> store
    ```

- space
  - post fin `! store -> tail -> continue` implies `not run_done`

- meta script
  - daily init
  - launch next
  - daily fin
  - daily report

- finish square questioning work
