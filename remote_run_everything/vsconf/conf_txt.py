def tasks_rs():
    return '''
    {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "cargo run",
            "type": "shell",
            "command": "~/.cargo/bin/cargo", // note: full path to the cargo
            "args": [
                // "run",
                "test",
                "--",
                "--nocapture",
                // "-D",
                // "warnings",
                // "--release",
                // "--",
                // "arg1"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        }
    ]
}
    '''


def launch_rs():
    return '''
   {
  "version": "0.2.0",
  "configurations": [
    {
      "name": "deb", // 调试配置名称（显示在下拉菜单）
      "type": "cppdbg", // 调试器类型（C/C++ 扩展提供）
      "request": "launch", // 启动新进程调试（区别于 attach）
      "program": "${workspaceFolder}/target/debug", // 调试目标路径
      "args": [], // 程序启动参数
      "preLaunchTask": "cargo run"
    }
  ]
} 
    '''
def git():
    return '''
# 首先忽略所有的文件
*
# 但是不忽略目录
!*/
# 忽略一些指定的目录名
**/node_modules/
**/target/
**/dist/
# 不忽略下面指定的文件类型
!*.vue
!*.js
!*.html
!*.css
!*.py
!*.rs
!*.go
!*.c
!*.cpp
    '''