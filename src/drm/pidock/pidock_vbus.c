#include <linux/device.h>

// static char *Version = "0.0.01";

static void pidock_bus_release(struct device *dev)
{
    printk(KERN_DEBUG "pidock release\n");
}

/*
struct pidock_device pidock_bus = {
	.device.bus_id = "pidock",
	.device.release = "pidock_bus_release,
}
*/

/*
struct device pidock_bus = {
    // .bus_id   = "pidock",
    .release  = pidock_bus_release
};

int pidock_device_init(void)
{
	int rc;

	pidock_vbus_register_device();

	return 0;
}

void pidock_device_cleanup(void)
{
	device_unregister(&pidock_bus);
}
*/

static int pidock_bus_match(struct device *dev, struct device_driver *drv)
{
	return 0;
}

/*
static int pidock_bus_uevent(struct device *dev, struct kobj_uevent_env *env)
{
	if (add_uevent_var(env, "PIDOCKBUS_VERSION=%s", Version))
		return -ENOMEM;

	return 0;
}
*/

struct device pidock_bus = {
	.init_name = "pidock0",
	.release  = pidock_bus_release
};

struct bus_type pidock_bus_type = {
	.name = "pidock",
	.match = pidock_bus_match,
//    .uevent  = pidock_bus_uevent,
//    .hotplug  = pidock_bus_hotplug,
};

/*
int pidock_bus_register_device(struct pidock_device *pdev)
{

	pdev->dev.bus = &pidock_bus_type;
	pdev->dev.parent = &pidock_bus;
	pdev->dev.release = pidock_device_release;
	dev_set_name(&pdev->dev, "pidock0");
	return device_register(&ldddev->dev);
}
*/


int pidock_bus_init(void)
{
	int rc;

    printk(KERN_INFO "pidock_bus_init:");

	rc = bus_register(&pidock_bus_type);
	if (rc) {
		printk(KERN_WARNING "pidock: bus_register error: %d\n", rc);
		return rc;
	}

	/*
	if (bus_create_file(&pidock_bus_type, &bus_attr_version))
		printk(KERN_NOTICE "Unable to create version attribute\n");
	*/

	rc = device_register(&pidock_bus);
	if (rc)
		printk(KERN_WARNING "Unable to register pidock0\n");

	return rc;
}

void pidock_bus_cleanup(void)
{
	device_unregister(&pidock_bus);
	bus_unregister(&pidock_bus_type);
}
