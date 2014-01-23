#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Напишите класс, реализующий функциональность маршрутизатора.
Атрибуты класса должны включать:
    1. Таблицу интерфейсов - словарь вида
    {'fa0/0':[address, mask], 'serial 0/0':[address, mask] и т.д.}
    2. Таблицу маршрутизации - список вида
    [[dstaddr, dstmask, nexthop],
            [dstaddr, dstmask, nexthop],
            [dstaddr, dstmask, nexthop]]

    Методы класса:
        ipAddr('interface', 'address', 'mask')
        Присваивание адреса интерфейсу, адрес и маска - в
        точечно-десятичной нотации
        ipRoute('destinationAddress', 'destinationMask', 'nextHopAddress')
        Добавление маршрута
        listIntr()
        Выводит список интерфейсов
        listRoutes()
        Выводит таблицу маршрутизации

        route(dstaddr)
        Возвращает кортеж вида: выходной интерфейс, адрес следующего перехода

        Стоимость задания - 70 баллов
'''
import struct
import socket


class IPv4Address(object):
    '''
        This class designated to easy manipulate ipv4 addresses and masks
    '''
    default_subnet_masks = (
        # network A class
        (
            0b10000000000000000000000000000000,  # check_value
            0b00000000000000000000000000000000,  # leading_bit
            0b11111111000000000000000000000000,  # mask
            '255.0.0.0'  # mask_dotted
        ),
        # network B class
        (
            0b11000000000000000000000000000000,
            0b10000000000000000000000000000000,
            0b11111111111111110000000000000000,
            '255.255.0.0'
        ),
        # network C class
        (
            0b11000000000000000000000000000000,
            0b11000000000000000000000000000000,
            0b11111111111111111111111100000000,
            '255.255.255.0'
        ),
    )

    def __init__(self, raw_addr, raw_mask=None):
        self.addr_decimal, self.addr_dotted = IPv4Address.parse(raw_addr)

        if raw_mask:
            parsed_mask = IPv4Address.parse_netmask(raw_mask)
        else:
            parsed_mask = IPv4Address.determine_mask_by_ip(self.addr_decimal)

        self.mask_decimal, self.mask_dotted = parsed_mask
        self.addr_decimal, self.addr_dotted = IPv4Address.parse(raw_addr)

    @staticmethod
    def determine_mask_by_ip(raw_addr):
        ''' determine class of network '''
        for default_subnet in IPv4Address.default_subnet_masks:
            (
                check_value,
                leading_bit,
                mask_decimal,
                mask_dotted
            ) = default_subnet
            # determine class of ip network
            if raw_addr & check_value == leading_bit:
                return (mask_decimal, mask_dotted)
        return (None, None)

    @staticmethod
    def parse(raw_addr):
        ''' try to parse raw_addr format '''
        if type(raw_addr) == str:
            return IPv4Address.parse_dotted(raw_addr)
        elif type(raw_addr) == int:
            return IPv4Address.parse_decimal(raw_addr)
        elif type(raw_addr) == IPv4Address:
            return raw_addr.decimal(), raw_addr.dotted()
        else:
            raise Exception('Can not parse ip address')

    @staticmethod
    def parse_dotted(addr_dotted):
        ''' try to parse ip address in dotted notation '''
        try:
            addr_decimal, = struct.unpack(
                '>I',
                socket.inet_aton(addr_dotted)
            )
            return (addr_decimal, addr_dotted)
        except:
            raise Exception('illegal IP address string passed as argument')

    @staticmethod
    def parse_decimal(addr_decimal):
        ''' try to parse ip address in decimal '''
        try:
            addr_dotted = socket.inet_ntoa(struct.pack('>I', addr_decimal))
            return (addr_decimal, addr_dotted)
        except:
            raise Exception('Illegal IP address value passed to method')

    def dotted(self):
        ''' return ipv4 address in dotted notation '''
        return self.addr_dotted

    def binary(self):
        ''' return binary repesentation of ipv4 address '''
        decimal_octets = self.dotted().split('.')
        binarify = lambda octet: bin(int(octet))[2:].zfill(8)
        octets = [binarify(octet) for octet in decimal_octets]
        return '.'.join(octets)

    def decimal(self):
        ''' return ipv4 as decimal value '''
        return self.addr_decimal

    @staticmethod
    def parse_netmask(mask):
        ''' try parse netmask '''
        return IPv4Address.parse(mask)

    def netmask_dotted(self):
        ''' return netmask in dotted represenation '''
        return self.mask_dotted

    def netmask_decimal(self):
        ''' return netmask as decimal value '''
        return self.mask_decimal

    def netmask(self):
        ''' return netmask in two represenation decimal and dotted '''
        return self.netmask_decimal(), self.netmask_dotted()

    def subnet(self):
        ''' calculate subnet from ipv4 address and mask '''
        if self.netmask_decimal():
            return self.__class__(
                self.netmask_decimal() & self.decimal(),
                self.netmask_decimal()
            )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.decimal() == other.decimal()
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __and__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.decimal() & other.decimal())
        else:
            return NotImplemented

    def __str__(self):
        return self.dotted()

    def __repr__(self):
        dotted = ', '.join(
            filter(bool, [self.dotted(), self.netmask_dotted()])
        )
        return "IPv4Address(%s)" % dotted


class Router(object):
    def __init__(self):
        self.iface_table = {}
        self.routes = []

    def ip_addr(self, interface, address, mask):
        ''' make it a rule: 1 ipv4 address per 1 interface '''
        ipv4_addr = IPv4Address(address, mask)

        # add route to directly connected network
        ipv4_directly_connected_network = ipv4_addr.subnet()
        self.ip_route(
            ipv4_directly_connected_network,
            ipv4_addr.netmask_decimal(),
            ipv4_addr
        )

        self.iface_table[interface] = ipv4_addr

    def ip_route(self, dest_addr, dest_mask, next_hop_addr):
        ''' add static route '''
        self.routes.append((
            IPv4Address(dest_addr),
            IPv4Address(dest_mask),
            IPv4Address(next_hop_addr)
        ))

    def get_iface_by_addr(self, addr):
        ''' determine interface name by ipv4 address '''
        for iface, iface_addr in self.iface_table.items():
            if addr == iface_addr:
                return iface

    def list_interfaces(self):
        ''' nice outputs interface list '''
        fmt = '%-15s%-15s%-15s'
        interface_repr = ('interface', 'ipv4 address', 'netmask')
        print fmt % interface_repr
        print "=" * 45
        for iface, addr in self.iface_table.items():
            print fmt % (
                iface,
                addr.dotted(),
                addr.netmask_dotted()
            )

    def list_routes(self):
        ''' nice outputs routes '''
        fmt = '%-15s%-15s%-15s'
        routes_repr = ('destination', 'mask', 'interface')
        print fmt % routes_repr
        print "=" * 45
        for route in self.routes:
            print fmt % route

    def route(self, addr):
        ''' find optimal route by longest prefix match '''
        ipv4_decimal = IPv4Address(addr).decimal()
        possible_routes = []
        for dest_addr, dest_mask, next_hop_addr in self.routes:
            subnet = dest_addr.decimal() & dest_mask.decimal()
            if ipv4_decimal & subnet == subnet:
                possible_routes.append((ipv4_decimal, subnet, next_hop_addr))

        # longest prefix match
        _, _, next_hop_addr = max(
            possible_routes,
            key=lambda route: route[2]
        )

        return self.get_iface_by_addr(next_hop_addr), next_hop_addr


def __main__():
    pass

if __name__ == '__main__':
    __main__()
