from . import Library, Interface, FLAPIException
import json

# SystemInfo
#
# Provides information about hardware, OS and software
#

class SystemInfo(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_hardware_info
    #
    # Return base hardware information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Hardware information
    #        'Manufacturer' (string): Hardware manufacturer
    #        'Model' (string): Hardware model
    #        'Motherboard' (string): Motherboard model
    #
    def get_hardware_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_hardware_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_hardware_info",
            {}
        )

    # get_os_info
    #
    # Return information about the OS installed in this system
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): OS version info
    #        'OSPlatform' (string): Platform is this software running on
    #        'OSVersion' (string): Version of operating system
    #
    def get_os_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_os_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_os_info",
            {}
        )

    # get_cpu_info
    #
    # Return CPU hardware information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): CPU Info
    #        'Model' (string): CPU Model
    #        'NumCores' (int): Total number of CPU cores
    #        'NumSockets' (int): Number of CPU sockets
    #        'Speed' (string): CPU Speed
    #
    def get_cpu_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_cpu_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_cpu_info",
            {}
        )

    # get_memory_info
    #
    # Return memory hardware information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Memory information
    #        'Total' (int): Total memory in megabytes
    #
    def get_memory_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_memory_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_memory_info",
            {}
        )

    # get_gpu_info
    #
    # Return GPU hardware information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of GPU information
    #        '<n>' (dict): GPU Information
    #            'Memory' (int): Memory size
    #            'Model' (string): Model name
    #
    def get_gpu_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_gpu_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_gpu_info",
            {}
        )

    # get_sdi_info
    #
    # Return SDI hardware information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (dict): SDI device information
    #            'Driver' (string): SDI driver version
    #            'Firmware' (string): SDI firmware version
    #            'ID' (string): SDI hardware model
    #            'Serial' (string): SDI hardware serial number
    #            'Type' (string): SDI hardware type
    #
    def get_sdi_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_sdi_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_sdi_info",
            {}
        )

    # get_network_info
    #
    # Return network interface information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): General network information
    #        'Hostname' (string): Network hostname
    #        'Interfaces' (list): Array of network interfaces
    #            '<n>' (dict): Interface information
    #                'Device' (string): Device name
    #                'IPv4Address' (list): Array of IPv4 addresses
    #                    '<n>' (string): IPv4 address
    #                'IPv4Mode' (string): Address mode: Manual, DHCP
    #                'Link' (int): Flag indicating that interface has a link
    #                'LinkSpeed' (string): Current link speed in MBbit/sec
    #                'MACAddress' (string): Ethernet MAC Address
    #                'Name' (string): Interface name
    #                'Running' (int): Flag indicating that interface is enabled
    #                'Speed' (string): Maximum link speed in Mbit/sec
    #        'ZCHostname' (string): Zeroconf hostname
    #
    def get_network_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_network_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_network_info",
            {}
        )

    # get_software_info
    #
    # Return array of installed applications
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (dict): Installed software information
    #            'Current' (int): Flag indicating that this is the currently active software version
    #            'Path' (string): Path to installed product
    #            'Product' (string): Product name
    #            'Version' (string): Product version
    #
    def get_software_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_software_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_software_info",
            {}
        )

    # switch_software_version
    #
    # Switch active software version
    #
    # Arguments:
    #    'product' (string): Product name
    #    'version' (string): Product version
    #
    # Returns:
    #    (none)
    #
    def switch_software_version(self, product, version):
        if self.target != None:
            raise FLAPIException( "Static method switch_software_version called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.switch_software_version",
            {
                'product': product,
                'version': version,
            }
        )

    # get_customer_info
    #
    # Return customer info dictionary (populated from preferences)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (CustomerInfo): 
    #
    def get_customer_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_customer_info called on instance of SystemInfo" )
        return self.conn.call(
            None,
            "SystemInfo.get_customer_info",
            {}
        )

Library.register_class( 'SystemInfo', SystemInfo )

