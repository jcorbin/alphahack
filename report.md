# 2025-09-06

- 🔗 spaceword.org 🧩 2025-09-05 🏗️ score 2168 current ranking 99/306 ⏱️ 6:24:21.475280

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

# spaceword.org 🧩 2025-09-05 🏗️ score 2168 current ranking 99/306 ⏱️ 6:24:21.475280

📜 4 sessions
- tiles: 21/21
- score: 2168 bonus: +68
- rank: 99/306

      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ V E G I E _ L _ _   
      _ _ _ H O G T I E _   
      _ Q U I N O A _ L _   
      _ _ _ _ _ _ J _ D _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   
      _ _ _ _ _ _ _ _ _ _   

