pidock-y := pidock_connector.o pidock_drv.o pidock_encoder.o pidock_fb.o pidock_gem.o pidock_main.o pidock_modeset.o pidock_nl.o pidock_output.o pidock_vbus.o
MY_CFLAGS += -g -DDEBUG
ccflags-y += ${MY_CFLAGS}
CC += ${MY_CFLAGS}

obj-m += pidock.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
