pidock-y := pidock_connector.o pidock_drv.o pidock_encoder.o pidock_fb.o pidock_gem.o pidock_main.o pidock_modeset.o pidock_nl.o pidock_vbus.o

obj-m += pidock.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
