import vulkan as vk

def debug_util_callback(severity, types, callback_data, user_data):
    print(callback_data.pMessageIdName)

def debug_report_callback(flags, object_type, object, location, message_code, layer_prefix, message, user_data):
    print(message)

class VkDevice:
    def __init__(self, physical_device, logical_device, graphics_queue_family_index):
        self.phsical_device = physical_device
        self.logical_device = logical_device
        self.graphics_queue_family_index = graphics_queue_family_index

class VkRenderer:
    def __init__(self, instance, device, debug_util_messenger, debug_report):
        self.instance = instance
        self.device = device
        self.debug_util_messenger = debug_util_messenger
        self.debug_report = debug_report

def init_vulkan():
    print("Initializing vulkan")

    application_info = vk.VkApplicationInfo(
        pApplicationName="Asset Viewer",
        applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
        pEngineName="Asset Viewer",
        engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
        apiVersion=vk.VK_API_VERSION_1_0
    )

    layer_props = vk.vkEnumerateInstanceLayerProperties()
    extension_props = vk.vkEnumerateInstanceExtensionProperties(None)

    has_validation_layer = False
    has_debug_util = False
    has_debug_report = False

    layers = []
    for layer_prop in layer_props:
        if layer_prop.layerName == "VK_LAYER_KHRONOS_validation":
            layers.append(layer_prop.layerName)
            has_validation_layer = True

    extensions = []
    if has_validation_layer:
        for extension_prop in extension_props:
            if extension_prop.extensionName == vk.VK_EXT_DEBUG_UTILS_EXTENSION_NAME:
                extensions.append(extension_prop.extensionName)
                has_debug_util = True
            elif extension_prop.extensionName == vk.VK_EXT_DEBUG_REPORT_EXTENSION_NAME:
                extensions.append(extension_prop.extensionName)
                has_debug_util = False

    instance_info = vk.VkInstanceCreateInfo(
        pApplicationInfo=application_info,
        ppEnabledLayerNames=layers,
        ppEnabledExtensionNames=extensions 
    )

    instance = vk.vkCreateInstance(instance_info, None)

    debug_util_messenger = None
    debug_report = None

    if has_debug_util:
        debug_util_messenger_info = vk.VkDebugUtilsMessengerCreateInfoEXT(
            messageType=vk.VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT|vk.VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT|vk.VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT,
            messageSeverity=vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT|vk.VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
            pfnUserCallback=debug_util_callback
        )

        vkCreateDebugUtilsMessengerEXT = vk.vkGetInstanceProcAddr(instance, "vkCreateDebugUtilsMessengerEXT")
        debug_util_messenger = vkCreateDebugUtilsMessengerEXT(instance, debug_util_messenger_info, None)
    elif has_debug_report:
        debug_report_callback_info = vk.VkDebugReportCallbackCreateInfoEXT(
            pfnCallback = debug_report_callback
        )

        vkCreateDebugReportCallbackEXT = vk.vkGetInstanceProcAddr(instance, "vkCreateDebugReportCallbackEXT")
        debug_report = vkCreateDebugReportCallbackEXT(instance, debug_report_callback_info, None) 

    physical_devices = vk.vkEnumeratePhysicalDevices(instance)

    device = None
    for physical_device in physical_devices:
        graphics_queue_family_index = -1
        queue_family_properties = vk.vkGetPhysicalDeviceQueueFamilyProperties(physical_device)

        for queue_family_index, queue_family_property in enumerate(queue_family_properties):
            if queue_family_property.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
                graphics_queue_family_index = queue_family_index
                break

        if graphics_queue_family_index != -1:
            queue_create_infos = [vk.VkDeviceQueueCreateInfo(
                queueFamilyIndex=graphics_queue_family_index,
                queueCount=1,
                pQueuePriorities=[1.0]
            )]

            device_info = vk.VkDeviceCreateInfo(
                pQueueCreateInfos=queue_create_infos
            )

            logical_device = vk.vkCreateDevice(physical_device, device_info, None)
            device = VkDevice(physical_device, logical_device, graphics_queue_family_index)


    if device == None:
        return None

    return VkRenderer(instance, device, debug_util_messenger, debug_report)