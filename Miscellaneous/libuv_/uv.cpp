#include <uv.h>
#include <iostream>



void timer_cb(uv_timer_t* timer, int status){
  std::cout << "timer callback\n";
}

void signal_cb(uv_signal_t* handle, int signum){
  std::cout << "Terminal size changed: " << signum << std::endl;
}

int main(){

  uv_loop_t* loop = uv_default_loop();

  uv_timer_t timer;
  uv_timer_init(loop,&timer);
  uv_timer_start(&timer,&timer_cb,0L,100000L);

  uv_signal_t signal;
  uv_signal_init(loop,&signal);
  uv_signal_start(&signal,&signal_cb,SIGWINCH);

  uv_run(loop, UV_RUN_DEFAULT);

  return 0;

}
