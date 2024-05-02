import json
import copy
import re

part1 = json.load(open('part1_final.json'))
part2 = json.load(open('part2_final.json'))
part3 = json.load(open('part3_final.json'))

ddr = json.load(open('ddr.json'))
hdmi = json.load(open('hdmi/regs.json'))
displayport = json.load(open('displayport/regs.json'))
pcie = json.load(open('pcie/regs.json'))
pd = json.load(open('parsed/009_PD_final.json'))
isp = json.load(open('parsed/005_ISP_final.json'))
typecphy = json.load(open('parsed/011_TCPHY_final.json'))

attrs = []
for group in part1 + part2 + part3 + pd + isp + typecphy:
    for register in group['registers']:
        for bit_range in register['bit_ranges']:
            attrs.append(bit_range['attr'].replace('\n', ''))
for register in ddr:
    for bit_range in register['bit_ranges']:
        attrs.append(bit_range['access'].replace('\n', ''))
for register in hdmi:
    for bit_range in register['bit_ranges']:
        attrs.append(bit_range['access'].replace('\n', ''))
for register in pcie:
    for bit_range in register['bit_ranges']:
        attrs.append(bit_range['sw'].replace('\n', ''))

device_maps = {
    "MSCH": [
        {
            "name": "MSCH0",
            "base": "0xffa84000",
            "description": "Memory Schedule (MSCH) 0 Registers",
        },
        {
            "name": "MSCH1",
            "base": "0xffa8c000",
            "description": "Memory Schedule (MSCH) 1 Registers",
        },
    ],
    "WDT": [
        {
            "name": "WDT0",
            "base": "0xFF848000",
            "description": "Watchdog Timer (WDT) 0 Registers",
        },
        {
            "name": "WDT1",
            "base": "0xFF840000",
            "description": "Watchdog Timer (WDT) 1 Registers",
        },
        {
            "name": "WDT2",
            "base": "0xFF380000",
            "description": "Watchdog Timer (WDT) 2 Registers",
        },
    ],
    "RKI2C": [
        {
            "name": "RKI2C0",
            "base": "0xFF3C0000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 0 Registers",
        },
        {
            "name": "RKI2C1",
            "base": "0xFF110000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 1 Registers",
        },
        {
            "name": "RKI2C2",
            "base": "0xFF120000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 2 Registers",
        },
        {
            "name": "RKI2C3",
            "base": "0xFF130000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 3 Registers",
        },
        {
            "name": "RKI2C4",
            "base": "0xFF3D0000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 4 Registers",
        },
        {
            "name": "RKI2C5",
            "base": "0xFF140000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 5 Registers",
        },
        {
            "name": "RKI2C6",
            "base": "0xFF150000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 6 Registers",
        },
        {
            "name": "RKI2C7",
            "base": "0xFF160000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 7 Registers",
        },
        {
            "name": "RKI2C8",
            "base": "0xFF3E0000",
            "description": "Rockchip Inter-Integrated Circuit (RKI2C) 8 Registers",
        },
    ],
    "PMUCRU": [
        {
            "name": "PMUCRU",
            "base": "0xFF750000",
            "description": "Power Management Unit Clock and Reset Unit (PMUCRU) Registers",
        }
    ],
    "SDMMC": [
        {
            "name": "SDMMC",
            "base": "0xFE320000",
            "description": "Secure Digital MultiMedia Card (SDMMC) Registers",
        },
    ],
    "GPIO": [
        {
            "name": "GPIO0",
            "base": "0xFF720000",
            "description": "General Purpose Input/Output (GPIO) 0 Registers",
        },
        {
            "name": "GPIO1",
            "base": "0xFF730000",
            "description": "General Purpose Input/Output (GPIO) 1 Registers",
        },
        {
            "name": "GPIO2",
            "base": "0xFF780000",
            "description": "General Purpose Input/Output (GPIO) 2 Registers",
        },
        {
            "name": "GPIO3",
            "base": "0xFF788000",
            "description": "General Purpose Input/Output (GPIO) 3 Registers",
        },
        {
            "name": "GPIO4",
            "base": "0xFF790000",
            "description": "General Purpose Input/Output (GPIO) 4 Registers",
        },
    ],
    "PMUGRF": [
        {
            "name": "PMUGRF",
            "base": "0xFF320000",
            "description": "Power Management Unit General Register File (PMUGRF) Registers",
        }
    ],
    "ERR_LOGGER_SLV": [
        {
            "name": "ERR_LOGGER_SLV0",
            "base": "0xffa64000",
            "description": "Error Logger (ERR_LOGGER) Registers for the paths from all masters except the PMU of the Cortex-M0 to all slaves outside the PMU power domain",
        },
        {
            "name": "ERR_LOGGER_SLV1",
            "base": "0xffa68080",
            "description": "Error Logger (ERR_LOGGER) Registers for the paths from the PMU of the Cortex-M0 to all slaves inside the PMU power domain",
        },
    ],
    "ERR_LOGGER_MSCH": [
        {
            "name": "ERR_LOGGER_MSCH0",
            "base": "0xffa87c80",
            "description": "Error Logger (ERR_LOGGER) Registers for the paths from all masters to the memory schedule 0",
        },
        {
            "name": "ERR_LOGGER_MSCH1",
            "base": "0xffa8fc80",
            "description": "Error Logger (ERR_LOGGER) Registers for the paths from all masters to the memory schedule 1",
        },
    ],
    "DDR_PI": [
        {
            "name": "DDR_PI0",
            "base": "0xffa80800",
            "description": "DDR PHY Independent 0 (DDR_PI0) Registers",
        },
        {
            "name": "DDR_PI1",
            "base": "0xffa88800",
            "description": "DDR PHY Independent 1 (DDR_PI1) Registers",
        },
    ],
    "DDR_CIC": [
        {
            "name": "DDR_CIC",
            "base": "0xff620000",
            "description": "DDR Controller Interface Control Registers (DDR_CIC) Registers",
        }
    ],
    "DDR_MON": [
        {
            "name": "DDR_MON",
            "base": "0xff630000",
            "description": "DDR Monitor (DDR_MON) Registers",
        }
    ],
    "USB3": [
        {
            "name": "USB3_OTG0",
            "base": "0xFE800000",
            "description": "USB 3.0/2.0 OTG Register 0 (USB3_OTG0) Registers",
        },
        {
            "name": "USB3_OTG1",
            "base": "0xFE900000",
            "description": "USB 3.0/2.0 OTG Register 1 (USB3_OTG1) Registers",
        },
    ],
    "MAILBOX": [
        {
            "name": "MAILBOX0",
            "base": "0xFF6B0000",
            "description": "Mailbox 0 Registers",
        },
        {
            "name": "MAILBOX1",
            "base": "0xFF390000",
            "description": "Mailbox 1 Registers",
        },
    ],
    "CRU": [
        {
            "name": "CRU",
            "base": "0xFF760000",
            "description": "Clock and Reset Unit (CRU) Registers",
        }
    ],
    "GMAC": [
        {
            "name": "GMAC",
            "base": "0xFE300000",
            "description": "Gigabit Media Access Controller (GMAC) Registers",
        }
    ],
    "UART": [
        {
            "name": "UART0",
            "base": "0xFF180000",
            "description": "Universal Asynchronous Receiver/Transmitter 0 (UART0) Registers",
        },
        {
            "name": "UART1",
            "base": "0xFF190000",
            "description": "Universal Asynchronous Receiver/Transmitter 1 (UART1) Registers",
        },
        {
            "name": "UART2",
            "base": "0xFF1A0000",
            "description": "Universal Asynchronous Receiver/Transmitter 2 (UART2) Registers",
        },
        {
            "name": "UART3",
            "base": "0xFF1B0000",
            "description": "Universal Asynchronous Receiver/Transmitter 3 (UART3) Registers",
        },
        {
            "name": "UART4",
            "base": "0xFF370000",
            "description": "Universal Asynchronous Receiver/Transmitter 4 (UART4) Registers",
        },
    ],
    "QOS": [
        {
            "name": "QOS_CCI_M0",
            "base": "0xffa50000",
            "description": "QoS Registers for CCI_M0",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_CCI_M1",
            "base": "0xffad8000",
            "description": "QoS Registers for CCI_M1",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_DMAC0",
            "base": "0xffa64200",
            "description": "QoS Registers for DMAC0",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_DMAC1",
            "base": "0xffa64280",
            "description": "QoS Registers for DMAC1",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_DCF",
            "base": "0xffa64180",
            "description": "QoS Registers for DCF",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_CRYPTO0",
            "base": "0xffa64100",
            "description": "QoS Registers for CRYPTO0",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_CRYPTO1",
            "base": "0xffa64080",
            "description": "QoS Registers for CRYPTO1",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_PMU_CM0",
            "base": "0xffa68000",
            "description": "QoS Registers for PMU_CM0",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_PERI_CM0",
            "base": "0xffa64300",
            "description": "QoS Registers for PERI_CM0",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_GIC",
            "base": "0xffa78000",
            "description": "QoS Registers for GIC",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_SDIO",
            "base": "0xffa76000",
            "description": "QoS Registers for SDIO",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_SDMMC",
            "base": "0xffa74000",
            "description": "QoS Registers for SDMMC",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_EMMC",
            "base": "0xffa58000",
            "description": "QoS Registers for EMMC",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_PCIE",
            "base": "0xffa60080",
            "description": "QoS Registers for PCIE",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_HSIC",
            "base": "0xffa60000",
            "description": "QoS Registers for HSIC",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_GMAC",
            "base": "0xffa5c000",
            "description": "QoS Registers for GMAC",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_USB_OTG0",
            "base": "0xffa70000",
            "description": "QoS Registers for USB_OTG0",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_USB_OTG1",
            "base": "0xffa70080",
            "description": "QoS Registers for USB_OTG1",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_USB_HOST0",
            "base": "0xffa60100",
            "description": "QoS Registers for USB_HOST0",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_USB_HOST1",
            "base": "0xffa60180",
            "description": "QoS Registers for USB_HOST1",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_GPU",
            "base": "0xffae0000",
            "description": "QoS Registers for GPU",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_VIDEO_M0",
            "base": "0xffab8000",
            "description": "QoS Registers for VIDEO_M0",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_VIDEO_M1_R",
            "base": "0xffac0000",
            "description": "QoS Registers for VIDEO_M1_R",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_VIDEO_M1_W",
            "base": "0xffac0080",
            "description": "QoS Registers for VIDEO_M1_W",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_RGA_R",
            "base": "0xffab0000",
            "description": "QoS Registers for RGA_R",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_RGA_W",
            "base": "0xffab0080",
            "description": "QoS Registers for RGA_W",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_IEP",
            "base": "0xffa98000",
            "description": "QoS Registers for IEP",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_VOP_BIG_R",
            "base": "0xffac8000",
            "description": "QoS Registers for VOP-BIG_R",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_VOP_BIG_W",
            "base": "0xffac8080",
            "description": "QoS Registers for VOP-BIG_W",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_VOP_LITTLE",
            "base": "0xffad0000",
            "description": "QoS Registers for VOP-LITTLE",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_ISP0_M0",
            "base": "0xffaa0000",
            "description": "QoS Registers for ISP0_M0",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_ISP0_M1",
            "base": "0xffaa0080",
            "description": "QoS Registers for ISP0_M1",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_ISP1_M0",
            "base": "0xffaa8000",
            "description": "QoS Registers for ISP1_M0",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_ISP1_M1",
            "base": "0xffaa8080",
            "description": "QoS Registers for ISP1_M1",
            "bandwidth_bits": "12",
        },
        {
            "name": "QOS_HDCP",
            "base": "0xffa90000",
            "description": "QoS Registers for HDCP",
            "bandwidth_bits": "11",
        },
        {
            "name": "QOS_PERIHP_NSP",
            "base": "0xffad8080",
            "description": "QoS Registers for PERIHP_NSP",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_PERILP_NSP",
            "base": "0xffad8180",
            "description": "QoS Registers for PERILP_NSP",
            "bandwidth_bits": "13",
        },
        {
            "name": "QOS_PERILPSLV_NSP",
            "base": "0xffad8100",
            "description": "QoS Registers for PERILPSLV_NSP",
            "bandwidth_bits": "11",
        },
    ],
    "EFUSE": [
        {
            "name": "EFUSE0",
            "base": "0xFF690000",
            "description": "eFuse 0 Registers",
        },
        {
            "name": "EFUSE1",
            "base": "0xFFFA0000",
            "description": "eFuse 1 Registers",
        },
    ],
    "EMMCCORE": [
        {
            "name": "EMMCCORE",
            "base": "0xFE330000",
            "description": "eMMC Controller (EMMCCORE) Registers",
        }
    ],
    "PROBE": [
        {
            "name": "PROBE_CCI_MSCH0",
            "base": "0xffa86000",
            "description": "Registers for the probe covering paths from the CCI_M1 to the memory schedule 0",
        },
        {
            "name": "PROBE_GPU_MSCH0",
            "base": "0xffa86400",
            "description": "Registers for the probe covering paths from the GPU to the memory schedule 0",
        },
        {
            "name": "PROBE_PERIHP_MSCH0",
            "base": "0xffa86800",
            "description": "Registers for the probe covering paths from the perihp master NIU to the memory schedule 0",
        },
        {
            "name": "PROBE_PERILP_MSCH0",
            "base": "0xffa86c00",
            "description": "Registers for the probe covering paths from the perilp master NIU, debug and CCI_M0 to the memory schedule 0",
        },
        {
            "name": "PROBE_VIDEO_MSCH0",
            "base": "0xffa87000",
            "description": "Registers for the probe covering paths from video to the memory schedule 0",
        },
        {
            "name": "PROBE_VIO0_MSCH0",
            "base": "0xffa87400",
            "description": "Registers for the probe covering paths from the IEP, ISP0 and VOP-BIG to the memory schedule 0",
        },
        {
            "name": "PROBE_VIO1_MSCH0",
            "base": "0xffa87800",
            "description": "Registers for the probe covering paths from the RGA, ISP1, VOP-LITTLE and HDCP to the memory schedule 0",
        },
        {
            "name": "PROBE_CCI_MSCH1",
            "base": "0xffa8e000",
            "description": "Registers for the probe covering paths from the CCI_M1 to the memory schedule 1",
        },
        {
            "name": "PROBE_GPU_MSCH1",
            "base": "0xffa8e400",
            "description": "Registers for the probe covering paths from the GPU to the memory schedule 1",
        },
        {
            "name": "PROBE_PERIHP_MSCH1",
            "base": "0xffa8e800",
            "description": "Registers for the probe covering paths from the perihp master NIU to the memory schedule 1",
        },
        {
            "name": "PROBE_PERILP_MSCH1",
            "base": "0xffa8ec00",
            "description": "Registers for the probe covering paths from the perilp master NIU, debug and CCI_M0 to the memory schedule 1",
        },
        {
            "name": "PROBE_VIDEO_MSCH1",
            "base": "0xffa8f000",
            "description": "Registers for the probe covering paths from video to the memory schedule 1",
        },
        {
            "name": "PROBE_VIO0_MSCH1",
            "base": "0xffa8f400",
            "description": "Registers for the probe covering paths from the IEP, ISP0 and VOP-BIG to the memory schedule 1",
        },
        {
            "name": "PROBE_VIO1_MSCH1",
            "base": "0xffa8f800",
            "description": "Registers for the probe covering paths from the RGA, ISP1, VOP-LITTLE and HDCP to the memory schedule 1",
        },
    ],
    "DMAC": [
        {
            "name": "DMAC0",
            "base": "0xFF6D0000",
            "description": "DMA Controller 0 Registers",
        },
        {
            "name": "DMAC1",
            "base": "0xFF6E0000",
            "description": "DMA Controller 1 Registers",
        },
    ],
    "TSADC": [
        {
            "name": "TSADC",
            "base": "0xFF260000",
            "description": "Temperature Sensor Analog-to-Digital Converter (TSADC) Registers",
        }
    ],
    "MMU": [
        {"name": "MMU0_ISP0", "base": "0xff914000", "description": "Registers of Memory Management Unit 0 (MMU0) for Image Signal Processor 0 (ISP0)"},
        {"name": "MMU1_ISP0", "base": "0xff915000", "description": "Registers of Memory Management Unit 1 (MMU1) for Image Signal Processor 0 (ISP0)"},
        {"name": "MMU0_ISP1", "base": "0xff924000", "description": "Registers of Memory Management Unit 0 (MMU0) for Image Signal Processor 1 (ISP1)"},
        {"name": "MMU1_ISP1", "base": "0xff925000", "description": "Registers of Memory Management Unit 1 (MMU1) for Image Signal Processor 1 (ISP1)"},
        {"name": "MMU_VOPB", "base": "0xff903f00", "description": "Registers of Memory Management Unit (MMU) for Visual Output Processor (Big) (VOPB)"},
        {"name": "MMU_VOPL", "base": "0xff8f3f00", "description": "Registers of Memory Management Unit (MMU) for Visual Output Processor (Little) (VOPL)"},
        {"name": "MMU_IEP", "base": "0xff670800", "description": "Registers of Memory Management Unit (MMU) for Image Enhancement Processor (IEP)"},
        {"name": "MMU_HDCP", "base": "0xff930000", "description": "Registers of Memory Management Unit (MMU) for High-bandwidth Digital Content Protection (HDCP)"},
        {"name": "MMU_RKVDEC_R", "base": "0xff660480", "description": "Registers of Memory Management Unit (MMU) for Rockchip Video Decoder (RKVDEC) Read"},
        {"name": "MMU_RKVDEC_W", "base": "0xff6604c0", "description": "Registers of Memory Management Unit (MMU) for Rockchip Video Decoder (RKVDEC) Write"},
        {"name": "MMU_VPU", "base": "0xff650800", "description": "Registers of Memory Management Unit (MMU) for Video Processing Unit (VPU)"},
    ],
    "CCI500": [
        {"name": "CCI500", "base": "0xFFB00000", "description": "Cache Coherent Interconnect 500 (CCI500) Registers"},
    ],
    "TIMER": [
        {"name": "TIMER0", "base": "0xff850000", "description": "Timer 0 Registers"},
        {"name": "TIMER1", "base": "0xff850020", "description": "Timer 1 Registers"},
        {"name": "TIMER2", "base": "0xff850040", "description": "Timer 2 Registers"},
        {"name": "TIMER3", "base": "0xff850060", "description": "Timer 3 Registers"},
        {"name": "TIMER4", "base": "0xff850080", "description": "Timer 4 Registers"},
        {"name": "TIMER5", "base": "0xff8500a0", "description": "Timer 5 Registers"},
        {"name": "TIMER6", "base": "0xff858000", "description": "Timer 6 Registers"},
        {"name": "TIMER7", "base": "0xff858020", "description": "Timer 7 Registers"},
        {"name": "TIMER8", "base": "0xff858040", "description": "Timer 8 Registers"},
        {"name": "TIMER9", "base": "0xff858060", "description": "Timer 9 Registers"},
        {"name": "TIMER10", "base": "0xff858080", "description": "Timer 10 Registers"},
        {"name": "TIMER11", "base": "0xff8580a0", "description": "Timer 11 Registers"},
        {"name": "STIMER0", "base": "0xff860000", "description": "Secure Timer 0 Registers"},
        {"name": "STIMER1", "base": "0xff860020", "description": "Secure Timer 1 Registers"},
        {"name": "STIMER2", "base": "0xff860040", "description": "Secure Timer 2 Registers"},
        {"name": "STIMER3", "base": "0xff860060", "description": "Secure Timer 3 Registers"},
        {"name": "STIMER4", "base": "0xff860080", "description": "Secure Timer 4 Registers"},
        {"name": "STIMER5", "base": "0xff8600a0", "description": "Secure Timer 5 Registers"},
        {"name": "STIMER6", "base": "0xff868000", "description": "Secure Timer 6 Registers"},
        {"name": "STIMER7", "base": "0xff868020", "description": "Secure Timer 7 Registers"},
        {"name": "STIMER8", "base": "0xff868040", "description": "Secure Timer 8 Registers"},
        {"name": "STIMER9", "base": "0xff868060", "description": "Secure Timer 9 Registers"},
        {"name": "STIMER10", "base": "0xff868080", "description": "Secure Timer 10 Registers"},
        {"name": "STIMER11", "base": "0xff8680a0", "description": "Secure Timer 11 Registers"},
        {"name": "PMUTIMER0", "base": "0xff360000", "description": "Power Management Unit Timer 0 Registers"},
        {"name": "PMUTIMER1", "base": "0xff360020", "description": "Power Management Unit Timer 1 Registers"},
    ],
    "PCIE_CLIENT": [
        {"name": "PCIE_CLIENT", "base": "0xFD000000", "description": "PCIe Client Registers"},
    ],
    "GRF": [
        {"name": "GRF", "base": "0xFF770000", "description": "General Register File (GRF) Registers"},
    ],
    "SPI": [
        {"name": "SPI0", "base": "0xFF1C0000", "description": "Serial Peripheral Interface (SPI) 0 Registers"},
        {"name": "SPI1", "base": "0xFF1D0000", "description": "Serial Peripheral Interface (SPI) 1 Registers"},
        {"name": "SPI2", "base": "0xFF1E0000", "description": "Serial Peripheral Interface (SPI) 2 Registers"},
        {"name": "SPI3", "base": "0xFF350000", "description": "Serial Peripheral Interface (SPI) 3 Registers"},
        {"name": "SPI4", "base": "0xFF1F0000", "description": "Serial Peripheral Interface (SPI) 4 Registers"},
        {"name": "SPI5", "base": "0xFF200000", "description": "Serial Peripheral Interface (SPI) 5 Registers"},
    ],
    "PMU": [
        {"name": "PMU", "base": "0xFF310000", "description": "Power Management Unit (PMU) Registers"},
    ],
    "I2S": [
        {"name": "I2S0", "base": "0xFF880000", "description": "Inter-IC Sound (I2S) 0 Registers"},
        {"name": "I2S1", "base": "0xFF890000", "description": "Inter-IC Sound (I2S) 1 Registers"},
        {"name": "I2S2", "base": "0xFF8A0000", "description": "Inter-IC Sound (I2S) 2 Registers"},
    ],
    "SARADC": [
        {"name": "SARADC", "base": "0xFF100000", "description": "Successive Approximation Register Analog-to-Digital Converter (SARADC) Registers"},
    ],
    "PWM": [
        {"name": "PWM", "base": "0xFF420000", "description": "Pulse Width Modulation (PWM) Registers"},
    ],
    "SPDIF": [
        {"name": "SPDIF", "base": "0xFF870000", "description": "Sony/Philips Digital Interface (SPDIF) Registers"},
    ],
    "RKVDEC": [
        {"name": "RKVDEC", "base": "0xFF660000", "description": "Rockchip Video Decoder (RKVDEC) Registers"},
    ],
    "VEPU": [
        {"name": "VEPU", "base": "0xFF650000", "description": "Video Processor Unit (VPU) Encoder Registers"},
    ],
    "VDPU": [
        {"name": "VDPU", "base": "0xFF650400", "description": "Video Processor Unit (VPU) Decoder Registers"},
    ],
    "PREF_CACHE": [
        {"name": "PREF_CACHE_RKVDEC_LUMA", "base": "0xFF660400", "description": "RKVDEC Luma Prefetch Cache Control Registers"},
        {"name": "PREF_CACHE_RKVDEC_CHROMA", "base": "0xFF660440", "description": "RKVDEC Chroma Prefetch Cache Control Registers"},
        {"name": "PREF_CACHE_VPU", "base": "0xFF650C00", "description": "VPU Prefetch Cache Control Registers"},
    ],
    "RGA2": [
        {"name": "RGA2", "base": "0xFF680000", "description": "Rockchip Graphics Accelerator 2 (RGA2) Registers"},
    ],
    "MIPI_DSI_HOST": [
        {"name": "MIPI_DSI_HOST0", "base": "0xFF960000", "description": "MIPI Display Serial Interface (DSI) Host 0 Registers"},
        {"name": "MIPI_DSI_HOST1", "base": "0xFF968000", "description": "MIPI Display Serial Interface (DSI) Host 1 Registers"},
    ],
    "DCF": [
        {"name": "DCF", "base": "0xFF6A0000", "description": "DDR Converser of Frequency (DCF) Registers"},
    ],
    "CRYPTO": [
        {"name": "CRYPTO0", "base": "0xFF8B0000", "description": "Crypto 0 Registers"},
        {"name": "CRYPTO1", "base": "0xFF8B8000", "description": "Crypto 1 Registers"},
    ],
    "VOPB": [
        {"name": "VOPB", "base": "0xFF900000", "description": "Visual Output Processor (Big) (VOPB) Registers"},
    ],
    "VOPL": [
        {"name": "VOPL", "base": "0xFF8F0000", "description": "Visual Output Processor (Little) (VOPL) Registers"},
    ],
    "IEP": [
        {"name": "IEP", "base": "0xFF670000", "description": "Image Enhancement Processor (IEP) Registers"},
    ],
    "TYPEC_PD": [
        {"name": "TYPEC_PD0", "base": "0xFF7A0000", "description": "Type-C Power Delivery (TYPEC_PD) 0 Registers"},
        {"name": "TYPEC_PD1", "base": "0xFF7B0000", "description": "Type-C Power Delivery (TYPEC_PD) 1 Registers"},
    ],
    "ISP": [
        {"name": "ISP0", "base": "0xFF910000", "description": "Image Signal Processor 0 (ISP0) Registers"},
        {"name": "ISP1", "base": "0xFF920000", "description": "Image Signal Processor 1 (ISP1) Registers"},
    ],
    "TYPEC_PHY": [
        {"name": "TYPEC_PHY0", "base": "0xFF7C0000", "description": "Type-C PHY 0 Registers"},
        {"name": "TYPEC_PHY1", "base": "0xFF800000", "description": "Type-C PHY 1 Registers"},
    ]
}

group_descriptions = {
    "MSCH": "Memory Schedule (MSCH) Registers",
    "WDT": "Watchdog Timer (WDT) Registers",
    "RKI2C": "Rockchip Inter-Integrated Circuit (RKI2C) Registers",
    "PMUCRU": "Power Management Unit Clock and Reset Unit (PMUCRU) Registers",
    "SDMMC": "Secure Digital MultiMedia Card (SDMMC) Registers",
    "GPIO": "General Purpose Input/Output (GPIO) Registers",
    "PMUGRF": "Power Management Unit General Register File (PMUGRF) Registers",
    "ERR_LOGGER_SLV": "Error Logger (ERR_LOGGER) Registers for the paths from all masters except the PMU of the Cortex-M0 to all slaves outside the PMU power domain",
    "ERR_LOGGER_MSCH": "Error Logger (ERR_LOGGER) Registers for the paths from all masters to the memory schedule",
    "DDR_PI": "DDR PHY Independent (DDR_PI) Registers",
    "DDR_CIC": "DDR Controller Interface Control (DDR_CIC) Registers",
    "DDR_MON": "DDR Monitor (DDR_MON) Registers",
    "USB3": "USB 3.0/2.0 OTG (USB3) Registers",
    "MAILBOX": "Mailbox Registers",
    "CRU": "Clock and Reset Unit (CRU) Registers",
    "GMAC": "Gigabit Media Access Controller (GMAC) Registers",
    "UART": "Universal Asynchronous Receiver/Transmitter (UART) Registers",
    "QOS": "Quality of Service (QOS) Registers",
    "EFUSE": "eFuse Registers",
    "EMMCCORE": "eMMC Controller (EMMCCORE) Registers",
    "PROBE": "Probe Registers",
    "DMAC": "DMA Controller (DMAC) Registers",
    "TSADC": "Temperature Sensor Analog-to-Digital Converter (TSADC) Registers",
    "MMU": "Memory Management Unit (MMU) Registers",
    "CCI500": "Cache Coherent Interconnect 500 (CCI500) Registers",
    "TIMER": "Timer Registers",
    "PCIE_CLIENT": "PCIe Client Registers",
    "GRF": "General Register File (GRF) Registers",
    "SPI": "Serial Peripheral Interface (SPI) Registers",
    "PMU": "Power Management Unit (PMU) Registers",
    "I2S": "Inter-IC Sound (I2S) Registers",
    "SARADC": "Successive Approximation Register Analog-to-Digital Converter (SARADC) Registers",
    "PWM": "Pulse Width Modulation (PWM) Registers",
    "SPDIF": "Sony/Philips Digital Interface (SPDIF) Registers",
    "RKVDEC": "Rockchip Video Decoder (RKVDEC) Registers",
    "VEPU": "Video Processor Unit (VPU) Encoder Registers",
    "VDPU": "Video Processor Unit (VPU) Decoder Registers",
    "PREF_CACHE": "VPU Prefetch Cache Registers",
    "RGA2": "Rockchip Graphics Accelerator 2 (RGA2) Registers",
    "MIPI_DSI_HOST": "MIPI Display Serial Interface (DSI) Host Registers",
    "DCF": "DDR Converser of Frequency (DCF) Registers",
    "CRYPTO": "Crypto Registers",
    "VOPB": "Visual Output Processor (Big) (VOPB) Registers",
    "VOPL": "Visual Output Processor (Little) (VOPL) Registers",
    "IEP": "Image Enhancement Processor (IEP) Registers",
    "TYPEC_PD": "Type-C Power Delivery (TYPEC_PD) Registers",
    "ISP": "Image Signal Processor (ISP) Registers",
    "TYPEC_PHY": "Type-C PHY Registers",
}

group_block_sizes = {
    "MSCH": "0x2000",
    "WDT": "0x8000",
    "RKI2C": "0x10000",
    "PMUCRU": "0x10000",
    "SDMMC": "0x10000",
    "GPIO": "0x8000",
    "PMUGRF": "0x10000",
    "ERR_LOGGER_SLV": "0x40",
    "ERR_LOGGER_MSCH": "0x40",
    "DDR_PI": "0x8000",
    "DDR_CIC": "0x10000",
    "DDR_MON": "0x10000",
    "USB3": "0x100000",
    "MAILBOX": "0x10000",
    "CRU": "0x10000",
    "GMAC": "0x10000",
    "UART": "0x10000",
    "QOS": "0x80",
    "EFUSE": "0x10000",
    "EMMCCORE": "0x10000",
    "PROBE": "0x400",
    "DMAC": "0x10000",
    "TSADC": "0x10000",
    "MMU": "0x40",
    "CCI500": "0x100000",
    "TIMER": "0x20",
    "PCIE_CLIENT": "0x800000",
    "GRF": "0x10000",
    "SPI": "0x10000",
    "PMU": "0x10000",
    "I2S": "0x10000",
    "SARADC": "0x10000",
    "PWM": "0x10000",
    "SPDIF": "0x10000",
    "RKVDEC": "0x400",
    "VEPU": "0x400",
    "VDPU": "0x400",
    "PREF_CACHE": "0x40",
    "RGA2": "0x10000",
    "MIPI_DSI_HOST": "0x8000",
    "DCF": "0x10000",
    "CRYPTO": "0x8000",
    "VOPB": "0x3000",
    "VOPL": "0x3000",
    "IEP": "0x800",
    "TYPEC_PD": "0x10000",
    "ISP": "0x4000",
    "TYPEC_PHY": "0x40000",
}

# (access, modifiedWriteValues, readAction)
svd_access_map = {
    'W': ('write-only', 'modify', None),
    'R/WOSET': ('read-write', 'oneToSet', None),
    'R/WOCLR': ('read-write', 'oneToClear', None),
    'RW': ('read-write', 'modify', None),
    'RU': ('read-only', None, None),
    'RW_D': ('read-write', 'modify', None),
    'R': ('read-only', None, None),
    'W1C': ('read-write', 'oneToClear', None),
    'WR': ('write-only', 'modify', None),
    'RD': ('read-only', None, None),
    'RO': ('read-only', None, None),
    'RC': ('read-only', None, 'clear'),
    'R/W': ('read-write', 'modify', None),
    'WO': ('write-only', 'modify', None),
    'R/W1C': ('read-write', 'oneToClear', None),
    'R/WSC': ('read-write', 'set', None),
    'RW+': ('read-write', 'modify', None),
    'RWW1toClr': ('read-write', 'oneToClear', None),
    'rw': ('read-write', 'modify', None),
    'r': ('read-only', None, None),
    'w': ('write-only', 'modify', None),
    'rwh': ('read-write', 'modify', None),
    'R/O': ('read-only', None, None),
}

peripherals = {}

for group in part1 + part2 + part3 + pd + isp + typecphy:
    device_map_groups = device_maps[group['name']]
    base_group = device_map_groups[0]
    if group['name'] not in peripherals:
        if group['name'] != base_group['name']:
            peripherals[group['name']] = {
                "name": group['name'],
                "baseAddress": base_group['base'],
                "description": group_descriptions[group['name']],
                "groupName": group['name'],
                "registers": [],
                "blockSize": group_block_sizes[group['name']],
            }
            peripherals[base_group['name']] = {
                "name": base_group['name'],
                "baseAddress": base_group['base'],
                "description": base_group['description'],
                "groupName": group['name'],
                "derivedFrom": group['name'],
                "alternatePeripheral": group['name'],
            }
        else:
            peripherals[base_group['name']] = {
                "name": base_group['name'],
                "baseAddress": base_group['base'],
                "description": base_group['description'],
                "groupName": group['name'],
                "registers": [],
                "blockSize": group_block_sizes[group['name']],
            }
        for device_map_group in device_map_groups[1:]:
            peripherals[device_map_group['name']] = {
                "name": device_map_group['name'],
                "baseAddress": device_map_group['base'],
                "description": device_map_group['description'],
                "groupName": group['name'],
                "derivedFrom": group['name'],
            }
    for register in group['registers']:
        register['offset'] = register['offset'].replace(' ', '').replace('\n', '')
        if not re.match(r'^[a-zA-Z0-9_]+$', register['offset']):
            print('Offset error', register['name'], register['offset'])
        size = register['size']
        if size == 'W':
            size = '32'
        elif size == 'HW':
            size = '16'
        elif size == 'DW':
            size = '64'
        elif size == 'B':
            size = '8'
        elif size.isdigit():
            size = size
        else:
            print('Size error', register['name'], size)
        register_element = {
            "name": register['name'],
            "description": register['description'].replace('"', "'"),
            "addressOffset": register['offset'],
            "resetValue": register['reset'].replace(' ', '').replace('\n', ''),
            "size": size,
            "fields": []
        }
        for bit_range in register['bit_ranges']:
            access, modifiedWriteValues, readAction = svd_access_map[bit_range['attr'].replace('\n', '')]
            bit_range['bit_range'] = bit_range['bit_range'].replace(' ', '').replace('\n', '')
            field_element = {
                "name": bit_range['name'].replace(' ', '_'),
                "description": bit_range['description'].replace('"', "'"),
                "bitRange": f"[{bit_range['bit_range']}]",
                "access": access,
                "resetValue": bit_range['reset']
            }
            if register['name'] == "QOS_Bandwidth":
                if bit_range['name'] == "RESERVED":
                    field_element["bitRange"] = f'[31:{int(base_group["bandwidth_bits"])}]'
                else:
                    field_element["bitRange"] = f'[{int(base_group["bandwidth_bits"])-1}:0]'
            if not re.match(r'^[0-9:]+$', bit_range['bit_range']):
                print('Bit range error', bit_range['name'], bit_range['bit_range'])
            if modifiedWriteValues:
                field_element["modifiedWriteValues"] = modifiedWriteValues
            if readAction:
                field_element["readAction"] = readAction
            register_element["fields"].append(field_element)
        if register_element['name'].startswith('USB3_DEPn'):
            register_element['name'] = register_element['name'].replace('USB3_DEPn', 'USB3_DEP%s')
            register_element['dim'] = "13"
            register_element['dimIncrement'] = "16"
            register_element['addressOffset'] = register_element['addressOffset'].split('~')[0]
        elif register_element['name'] == "PWM_PWM_FIFO":
            register_element['name'] = "PWM_PWM_FIFO%s"
            register_element['dim'] = "8"
            register_element['dimIncrement'] = "4"
            register_element['addressOffset'] = register_element['addressOffset'].split('~')[0]
        elif register_element['name'] == 'RX_BUF_OBJX_BYTE_3210':
            register_element['name'] = 'RX_BUF_OBJ%s_BYTE_3210'
            register_element['dim'] = "7"
            register_element['dimIndex'] = "1-7"
            register_element['dimIncrement'] = "4"
            register_element['addressOffset'] = register_element['addressOffset']
        elif register_element['name'] == 'TX_BUF_OBJX_BYTE_3210':
            register_element['name'] = 'TX_BUF_OBJ%s_BYTE_3210'
            register_element['dim'] = "7"
            register_element['dimIndex'] = "1-7"
            register_element['dimIncrement'] = "4"
            register_element['addressOffset'] = register_element['addressOffset']
        elif register_element['name'] in ['ISP_GAMMA_R_Y', 'ISP_GAMMA_G_Y', 'ISP_GAMMA_B_Y', 'ISP_GAMMA_OUT_Y', 'ISP_DPF_NLL_COEFF', 'ISP_WDR_TONECURVE_YM', 'ISP_WDR_TONECURVE_YM_SHD', 'ISP_CT_COEFF', 'ISP_HIST_BIN']:
            register_element['name'] = register_element['name'] + '_%s'
            register_element['dim'] = "17"
            if register_element['name'] == 'ISP_CT_COEFF_%s':
                register_element['dim'] = "9"
            elif register_element['name'] == 'ISP_HIST_BIN_%s':
                register_element['dim'] = "16"
            elif 'ISP_WDR_TONECURVE_YM' in register_element['name']:
                register_element['dim'] = "33"
            register_element['dimIncrement'] = "4"
            register_element['addressOffset'] = register_element['addressOffset']
        elif '~' in register_element['name'] or '-' in register_element['name']:
            start, end = None, None
            if re.match(r'^.*\d+~\d+$', register_element['name']):
                matches = re.match(r'^.*(\d+)~(\d+)$', register_element['name'])
                start, end = matches.groups()
                register_element['name'] = re.sub(r'\d+~\d+$', '%s', register_element['name'])
            elif re.match(r'^.*\d+[~\-].*\d+$', register_element['name']):
                matches = re.match(r'^.*(\d+)[~\-].*(\d+)$', register_element['name'])
                start, end = matches.groups()
                register_element['name'] = re.sub(r'\d+[~\-].*\d+$', '%s', register_element['name'])
            else:
                print('Invalid range', register_element['name'])
            register_element['dim'] = str(int(end) - int(start) + 1)
            if group['name'] == "DMAC":
                if 'FTR' in register_element['name']:
                    register_element['dimIncrement'] = "0x4"
                elif 'CSR' in register_element['name'] or 'CPC' in register_element['name']:
                    register_element['dimIncrement'] = "0x8"
                else:
                    register_element['dimIncrement'] = "0x20"
            else:
                register_element['dimIncrement'] = "0x4"
            register_element['dimIndex'] = f"{start}-{end}"
            register_element['addressOffset'] = register_element['addressOffset'].split('~')[0].split('-')[0]
        exceptions = ['DDRMON', 'CIC', 'ERRLOG']
        if register_element['name'].startswith(group['name'] + '_'):
            register_element['name'] = register_element['name'][len(group['name']) + 1:]
        else:
            for exception in exceptions:
                if register_element['name'].startswith(exception + '_'):
                    register_element['name'] = register_element['name'][len(exception) + 1:]
                    break
        peripherals[group['name']]['registers'].append(register_element)


ddrc_element = {
    "name": "DDRC",
    "baseAddress": "0xffa80000",
    "description": "DDR Controller (DDRC) Registers",
    "groupName": "DDR",
    "blockSize": "0x4000",
    "registers": [],
}
for register in ddr:
    if register['base'] == "CTL_BASE_ADDR":
        offset = hex(int(register['offset'], 16) * 4)
    elif register['base'] == "PHY_BASE_ADDR":
        offset = hex((int(register['offset'], 16)) * 4 + 0x2000)
    elif register['base'] == "PHY_AC_BASE_ADDR":
        offset = hex((int(register['offset'], 16) + 896) * 4 + 0x2000)
    register_element = {
        "name": register['name'],
        "description": "",
        "addressOffset": offset,
        "resetValue": "CALC",
        "fields": []
    }
    for bit_range in register['bit_ranges']:
        access, modifiedWriteValues, readAction = svd_access_map[bit_range['access'].replace('\n', '')]
        field_name = bit_range['name']
        field_name = re.sub(r' ?\[.*\]', '', field_name)
        field_element = {
            "name": field_name,
            "description": bit_range['description'].replace('"', "'"),
            "bitRange": f"[{bit_range['bits']}]",
            "access": access,
            "resetValue": bit_range['default'] if bit_range['default'] != 'Calc Value' else '0x0',
            "writeConstraint": {
                "range": {
                    "minimum": bit_range['range'].split('-')[0],
                    "maximum": bit_range['range'].split('-')[-1],
                }
            }
        }
        if modifiedWriteValues:
            field_element["modifiedWriteValues"] = modifiedWriteValues
        if readAction:
            field_element["readAction"] = readAction
        register_element["fields"].append(field_element)
    ddrc_element['registers'].append(register_element)
for register in peripherals['DDR_PI']['registers']:
    register['name'] = 'DDR_' + register['name']
    register['addressOffset'] = hex((int(register['addressOffset'], 16)) + 0x800)
    ddrc_element['registers'].append(register.copy())
peripherals['DDRC'] = ddrc_element
del peripherals['DDR_PI']
del peripherals['DDR_PI0']
del peripherals['DDR_PI1']
peripherals['DDRC0'] = {
    "name": "DDRC0",
    "baseAddress": "0xffa80000",
    "description": "DDR Controller 0 (DDRC0) Registers",
    "groupName": "DDR",
    "derivedFrom": "DDRC",
    "alternatePeripheral": "DDRC",
}
peripherals['DDRC1'] = {
    "name": "DDRC1",
    "baseAddress": "0xffa88000",
    "description": "DDR Controller 1 (DDRC1) Registers",
    "groupName": "DDR",
    "derivedFrom": "DDRC",
}

import json

prev_idx = 0
idx = 0
pcie_groups = json.load(open('pcie/reg_cats.json'))
pcie_core_element = {
    "name": "PCIE_CORE",
    "baseAddress": "0xfd800000",
    "description": "PCIe Core Registers",
    "groupName": "PCIE",
    "size": "32",
    "blockSize": "0x800000",
    "registers": [],
}
for group in pcie_groups:
    peripheral_element = {
        "name": group['name'],
        "baseAddress": group['base'],
        "description": group['description'],
        "groupName": "PCIE",
        "size": "32",
        "registers": [],
    }
    while idx < len(pcie) - 1 and pcie[idx]['name'] != group['last']:
        idx += 1
    registers = pcie[prev_idx:idx+1]
    prev_idx = idx + 1
    for register in registers:
        if '..' in register['address'] or register['name'].lower() == 'reserved':
            continue
        address = register['address'].replace(' ', '').replace('\n', '').replace('@', '')
        addressOffset = hex(int(address, 16) + int(group['base'], 16) - int(pcie_core_element['baseAddress'], 16))
        name = register['name'].replace('/', '_').replace('(' , '').replace(')', '').replace(',', '').replace('\n', '').replace(' ', '').replace('.', '')
        if not name.startswith(group['name'] + '_'):
            name = group['name'] + '_' + name
        register_element = {
            "name": name,
            "description": register['description'].replace('"', "'").strip(),
            "addressOffset": addressOffset,
            "resetValue": "CALC",
            "fields": []
        }
        if not re.match(r'^[a-zA-Z0-9_]+$', register_element['addressOffset']):
            print('Offset', re.escape(register['name']), register_element['addressOffset'])
        if not re.match(r'^[a-zA-Z0-9_]+$', register_element['name']):
            print('Name', re.escape(register['name']))
        for bit_range in register['bit_ranges']:
            if bit_range['name'].lower() in ['reserved', 'rsvd']:
                continue
            access, modifiedWriteValues, readAction = svd_access_map[bit_range['sw'].replace('\n', '')]
            reset = bit_range['reset']
            if not reset or 'Description' in reset:
                reset = "0x0"
            reset = re.sub(r"^[0-9]+'h", "0x", reset)
            reset = re.sub(r"^[0-9]+'d", "", reset)
            reset = re.sub(r"^[0-9]+'b", "0b", reset)
            reset = re.sub(r"^[0-9]+'o", "0o", reset)
            try:
                reset = hex(eval(reset))
            except Exception as e:
                print(register['name'], bit_range['name'], reset)
                raise e
            field_element = {
                "name": bit_range['name'].replace('/', '_').replace('(' , '').replace(')', '').replace(',', '').replace('\n', '').replace(' ', '').replace('.', ''),
                "description": bit_range['description'].replace('"', "'"),
                "bitRange": f"[{bit_range['bits']}]",
                "access": access,
                "resetValue": reset
            }
            if not re.match(r'^[0-9:]+$', bit_range['bits']):
                print('Bits', bit_range['name'], bit_range['bits'])
            if not re.match(r'^[a-zA-Z0-9_]+$', field_element['name']):
                print('Range Name', bit_range['name'], bit_range['bits'])
            if modifiedWriteValues:
                field_element["modifiedWriteValues"] = modifiedWriteValues
            if readAction:
                field_element["readAction"] = readAction
            register_element["fields"].append(field_element)
        pcie_core_element['registers'].append(register_element)
peripherals['PCIE_CORE'] = pcie_core_element

dp_element = {
    "name": "DP",
    "baseAddress": "0xFEC00000",
    "description": "DisplayPort Registers",
    "groupName": "DP",
    "size": "32",
    "blockSize": "0x100000",
    "registers": [],
}
for register in displayport:
    name, address, description, reset_value = register['name'], register['address'], register['description'], register['reset_value']
    register_element = {
        "name": name,
        "description": description,
        "addressOffset": address.replace('Base+', ''),
        "resetValue": reset_value.replace('.', ''),
        "fields": []
    }
    for bit_range in register['bit_ranges']:
        if bit_range['name'] != '-':
            access_type = 'R/W'
            if 'C' in bit_range['name']:
                access_type = 'W1C'
                bit_range['name'] = bit_range['name'].replace('(C)', '')
            if '(RO)' in bit_range['name']:
                access_type = 'RO'
                bit_range['name'] = bit_range['name'].replace('(RO)', '')
            if '(R/O)' in bit_range['name']:
                access_type = 'RO'
                bit_range['name'] = bit_range['name'].replace('(R/O)', '')
            access, modifiedWriteValues, readAction = svd_access_map[access_type]
            initial_value = bit_range['initial_value'].lower()
            initial_value = re.sub(r"^[0-9]+'h", "0x", initial_value)
            initial_value = re.sub(r"^[0-9]+'d", "", initial_value)
            initial_value = re.sub(r"^[0-9]+'b", "0b", initial_value)
            initial_value = re.sub(r"^[0-9]+'o", "0o", initial_value)
            initial_value = initial_value.replace('_', '')
            if 'x' not in initial_value and 'b' not in initial_value and 'o' not in initial_value:
                initial_value = hex(int(initial_value, 16))
            try:
                initial_value = hex(eval(initial_value))
            except Exception as e:
                print(register['name'], bit_range['name'], initial_value)
                raise e
            field_name = bit_range['name']
            field_name = re.sub(r' ?\[.*\]', '', field_name)
            field_name = field_name.replace('~', '_')
            field_element = {
                "name": field_name,
                "description": bit_range['description'],
                "bitRange": bit_range['bits'].replace(' ', ''),
                "access": access,
                "resetValue": initial_value
            }
            if modifiedWriteValues:
                field_element["modifiedWriteValues"] = modifiedWriteValues
            if readAction:
                field_element["readAction"] = readAction
            register_element["fields"].append(field_element)
    if '~' in name and '~' in address:
        start_name, end_name = name.split('~')
        start_address, end_address = address.split('~')
        start_address = start_address.replace('Base+', '')
        end_address = end_address.replace('Base+', '')
        start_idx = re.findall(r'\d+$', start_name)[0]
        end_idx = re.findall(r'\d+$', end_name)[0]
        register_element['dim'] = str(int(end_idx) - int(start_idx) + 1)
        register_element['dimIncrement'] = '4'
        register_element['dimIndex'] = f'{start_idx}-{end_idx}'
        register_element['name'] = start_name.replace(start_idx, '') + '%s'
        register_element['addressOffset'] = start_address
    dp_element['registers'].append(register_element)
peripherals['DP'] = dp_element


hdmi_element = {
    "name": "HDMI",
    "baseAddress": "0xFF940000",
    "description": "HDMI Registers",
    "groupName": "HDMI",
    "blockSize": "0x20000",
    "registers": [],
}
for register in hdmi:
    name, description, size, offset = register['name'], register['description'], register['size'], register['offset']
    register_element = {
        "name": name,
        "description": description,
        "addressOffset": offset,
        "resetValue": "CALC",
        "size": str(size),
        "fields": []
    }
    for bit_range in register['bit_ranges']:
        access, modifiedWriteValues, readAction = svd_access_map[bit_range['access'].replace('\n', '')]
        reset = bit_range['reset_value']
        description = bit_range['description']
        if '?' in reset:
            reset = "0x0"
            description = description + '\nReset Value: ' + bit_range['reset_value']
        if not re.match(f'^[0-9a-fx]+$', reset):
            print(register['name'], bit_range['name'], reset)
        field_element = {
            "name": bit_range['name'].replace('/', '_').replace('(' , '').replace(')', '').replace(',', '').replace('\n', '').replace(' ', '').replace('.', ''),
            "description": description,
            "bitRange": f"[{bit_range['bit_range']}]",
            "access": access,
            "resetValue": reset
        }
        if modifiedWriteValues:
            field_element["modifiedWriteValues"] = modifiedWriteValues
        if readAction:
            field_element["readAction"] = readAction
        register_element["fields"].append(field_element)
    if '[' in register_element['name'] and ']' in register_element['name']:
        register_range = re.findall(r'\[(.*?)\]', register_element['name'])[0]
        start, end = register_range.split(':')
        start, end = int(start), int(end)
        size = end + 1
        register_element['dim'] = str(size)
        register_element['dimIncrement'] = '1'
        register_element['name'] = register_element['name'].replace(f'[{start}:{end}]', '').strip() + f'[%s]'
        i = 0
        register_element['addressOffset'] = hex(eval(register_element['addressOffset']))
    hdmi_element['registers'].append(register_element)
peripherals['HDMI'] = hdmi_element

json.dump(peripherals, open('peripherals.json', 'w'), indent=2)

import xml.etree.ElementTree as ET
import xml.dom.minidom

root = ET.Element('device', schemaVersion="1.3", xs_noNamespaceSchemaLocation="CMSIS-SVD_Schema_1_3.xsd")
ET.SubElement(root, 'name').text = 'RK3399'
ET.SubElement(root, 'version').text = '1'
ET.SubElement(root, 'description').text = 'Rockchip RK3399'
ET.SubElement(root, 'resetMask').text = '0xFFFFFFFF'
ET.SubElement(root, 'width').text = '64'
ET.SubElement(root, 'addressUnitBits').text = '8'
ET.SubElement(root, 'resetValue').text = '0'
ET.SubElement(root, 'size').text = '32'
cpu = ET.SubElement(root, 'cpu')
ET.SubElement(cpu, 'fpuPresent').text = '1'
ET.SubElement(cpu, 'mpuPresent').text = '1'
ET.SubElement(cpu, 'dcachePresent').text = '1'
ET.SubElement(cpu, 'name').text = 'CA72'
ET.SubElement(cpu, 'endian').text = 'little'
ET.SubElement(cpu, 'vtorPresent').text = '1'
ET.SubElement(cpu, 'nvicPrioBits').text = '4'
ET.SubElement(cpu, 'vendorSystickConfig').text = '0'
ET.SubElement(cpu, 'icachePresent').text = '1'
ET.SubElement(cpu, 'revision').text = 'r0p1'
ET.SubElement(cpu, 'deviceNumInterrupts').text = '172'


peripherals_element = ET.SubElement(root, 'peripherals')
interrupts = json.load(open('interrupts.json'))
# peripherals = {p: x for p, x in sorted(peripherals.items(), key=lambda x: 'TIMERS' + x[0] if x[0].startswith('PMUTIMER') or x[0].startswith('STIMER') else x[0])}

# ordered = ['CCI500', 'CRU', 'DDRC', 'DDRC0', 'DDRC1', 'DDR_CIC', 'DDR_MON', 'DMAC', 'DMAC0', 'DMAC1', 'DP', 'EFUSE', 'EFUSE0', 'EFUSE1', 'EMMCCORE', 'ERR_LOGGER_MSCH', 'ERR_LOGGER_MSCH0', 'ERR_LOGGER_MSCH1', 'ERR_LOGGER_SLV', 'ERR_LOGGER_SLV0', 'ERR_LOGGER_SLV1', 'GMAC', 'GPIO', 'GPIO0', 'GPIO1', 'GPIO2', 'GPIO3', 'GPIO4', 'GRF', 'HDMI', 'I2S', 'I2S0', 'I2S1', 'I2S2', 'MAILBOX', 'MAILBOX0', 'MAILBOX1', 'MMU', 'MMU0_ISP0', 'MMU0_ISP1', 'MMU1_ISP0', 'MMU1_ISP1', 'MMU_HDCP', 'MMU_IEP', 'MMU_VOPB', 'MMU_VOPL', 'MSCH', 'MSCH0', 'MSCH1', 'PCIE_CLIENT', 'PCIE_CORE', 'PMU', 'PMUCRU', 'PMUGRF', 'PROBE', 'PROBE_CCI_MSCH0', 'PROBE_CCI_MSCH1', 'PROBE_GPU_MSCH0', 'PROBE_GPU_MSCH1', 'PROBE_PERIHP_MSCH0', 'PROBE_PERIHP_MSCH1', 'PROBE_PERILP_MSCH0', 'PROBE_PERILP_MSCH1', 'PROBE_VIDEO_MSCH0', 'PROBE_VIDEO_MSCH1', 'PROBE_VIO0_MSCH0', 'PROBE_VIO0_MSCH1', 'PROBE_VIO1_MSCH0', 'PROBE_VIO1_MSCH1', 'PWM', 'QOS', 'QOS_CCI_M0', 'QOS_CCI_M1', 'QOS_CRYPTO0', 'QOS_CRYPTO1', 'QOS_DCF', 'QOS_DMAC0', 'QOS_DMAC1', 'QOS_EMMC', 'QOS_GIC', 'QOS_GMAC', 'QOS_GPU', 'QOS_HDCP', 'QOS_HSIC', 'QOS_IEP', 'QOS_ISP0_M0', 'QOS_ISP0_M1', 'QOS_ISP1_M0', 'QOS_ISP1_M1', 'QOS_PCIE', 'QOS_PERIHP_NSP', 'QOS_PERILPSLV_NSP', 'QOS_PERILP_NSP', 'QOS_PERI_CM0', 'QOS_PMU_CM0', 'QOS_RGA_R', 'QOS_RGA_W', 'QOS_SDIO', 'QOS_SDMMC', 'QOS_USB_HOST0', 'QOS_USB_HOST1', 'QOS_USB_OTG0', 'QOS_USB_OTG1', 'QOS_VIDEO_M0', 'QOS_VIDEO_M1_R', 'QOS_VIDEO_M1_W', 'QOS_VOP_BIG_R', 'QOS_VOP_BIG_W', 'QOS_VOP_LITTLE', 'RKI2C', 'RKI2C0', 'RKI2C1', 'RKI2C2', 'RKI2C3', 'RKI2C4', 'RKI2C5', 'RKI2C6', 'RKI2C7', 'RKI2C8', 'SARADC', 'SDMMC', 'SPDIF', 'SPI', 'SPI0', 'SPI1', 'SPI2', 'SPI3', 'SPI4', 'SPI5', 'TIMER', 'TIMER0', 'TIMER1', 'TIMER2', 'TIMER3', 'TIMER4', 'TIMER5', 'TIMER6', 'TIMER7', 'TIMER8', 'TIMER9', 'TIMER10', 'TIMER11', 'STIMER0', 'STIMER1', 'STIMER2', 'STIMER3', 'STIMER4', 'STIMER5', 'STIMER6', 'STIMER7', 'STIMER8', 'STIMER9', 'STIMER10', 'STIMER11', 'PMUTIMER0', 'PMUTIMER1', 'TSADC', 'UART', 'UART0', 'UART1', 'UART2', 'UART3', 'UART4', 'USB3', 'USB3_OTG0', 'USB3_OTG1', 'WDT', 'WDT0', 'WDT1', 'WDT2']
# print(ordered)
# print(list(sorted(peripherals.keys(), key=lambda x: 'TIMER' + x if 'STIMER' in x or 'PMUTIMER' in x else x)))
peripherals = {p: x for p, x in sorted(peripherals.items(), key=lambda x: 'TIMER' + x[0] if 'STIMER' in x[0] or 'PMUTIMER' in x[0] else x[0])}
for peripheral in peripherals:
    if 'derivedFrom' in peripherals[peripheral]:
        peripheral_element = ET.SubElement(peripherals_element, 'peripheral', derivedFrom=peripherals[peripheral]['derivedFrom'])
        ET.SubElement(peripheral_element, 'name').text = peripherals[peripheral]['name']
        ET.SubElement(peripheral_element, 'baseAddress').text = peripherals[peripheral]['baseAddress']
        ET.SubElement(peripheral_element, 'description').text = peripherals[peripheral]['description'].replace('\n', '\\n\\n')
        ET.SubElement(peripheral_element, 'groupName').text = peripherals[peripheral]['groupName']
        if 'alternatePeripheral' in peripherals[peripheral]:
            ET.SubElement(peripheral_element, 'alternatePeripheral').text = peripherals[peripheral]['alternatePeripheral']
        # address_block = ET.SubElement(peripheral_element, 'addressBlock')
        # ET.SubElement(address_block, 'offset').text = '0'
        # ET.SubElement(address_block, 'size').text = '0x1000'
        # ET.SubElement(address_block, 'usage').text = 'registers'
    else:
        peripheral_element = ET.SubElement(peripherals_element, 'peripheral')
        ET.SubElement(peripheral_element, 'name').text = peripherals[peripheral]['name']
        ET.SubElement(peripheral_element, 'baseAddress').text = peripherals[peripheral]['baseAddress']
        ET.SubElement(peripheral_element, 'description').text = peripherals[peripheral]['description']
        ET.SubElement(peripheral_element, 'groupName').text = peripherals[peripheral]['groupName']
        address_block = ET.SubElement(peripheral_element, 'addressBlock')
        ET.SubElement(address_block, 'offset').text = '0'
        ET.SubElement(address_block, 'size').text = peripherals[peripheral]['blockSize']
        ET.SubElement(address_block, 'usage').text = 'registers'
        if 'size' in peripherals[peripheral]:
            size = int(peripherals[peripheral]['size'])
            ET.SubElement(peripheral_element, 'size').text = peripherals[peripheral]['size']
        registers_element = ET.SubElement(peripheral_element, 'registers')
        for r, register in enumerate(peripherals[peripheral]['registers']):
            if sum('reserved' in field['name'].lower() or 'reserve_' in field['name'].lower() for field in register['fields']) == len(register['fields']):
                continue
            register_element = ET.SubElement(registers_element, 'register')
            ET.SubElement(register_element, 'name').text = register['name']
            ET.SubElement(register_element, 'description').text = register['description'].replace('\n', '\\n\\n')
            ET.SubElement(register_element, 'addressOffset').text = register['addressOffset']
            if register['addressOffset'] == peripherals[peripheral]['registers'][r - 1]['addressOffset']:
                ET.SubElement(register_element, 'alternateRegister').text = peripherals[peripheral]['registers'][r - 1]['name']
            if 'size' in register:
                size = int(register['size'])
                ET.SubElement(register_element, 'size').text = register['size']
            if 'dim' in register:
                ET.SubElement(register_element, 'dim').text = register['dim']
                ET.SubElement(register_element, 'dimIncrement').text = register['dimIncrement']
                if 'dimIndex' in register:
                    ET.SubElement(register_element, 'dimIndex').text = register['dimIndex']
            if 'resetValue' in register and register['resetValue'] != 'CALC':
                reset_value = register['resetValue']
            else:
                reset_value = list('0' * size)
            if len(register['fields']) > 0:
                fields_element = ET.SubElement(register_element, 'fields')
            for i, field in enumerate(register['fields']):
                if 'reserved' in field['name'].lower() or 'reserve_' in field['name'].lower():
                    continue
                field_element = ET.SubElement(fields_element, 'field')
                field_name = field['name'] if field['name'] else f'{register["name"].replace("%s", "")}_BITS_{i}'
                if '%s' in field_name:
                    print(register['name'], field['name'])
                ET.SubElement(field_element, 'name').text = field_name
                lines = field['description'].split('\n')
                is_enum = []
                for line in lines:
                    if re.match(r"^\d+'?[bodh]?[0-9a-fA-FxbhXBh ]*:.*$", line):
                        is_enum.append(True)
                    else:
                        is_enum.append(False)
                enums = []
                non_enums = []
                for i, line in enumerate(lines):
                    if is_enum[i]:
                        enums.append(line)
                    else:
                        if enums:
                            enums[-1] += ' ' + line
                        else:
                            non_enums.append(line)
                # enum_exclusions = ['DP_TEST', 'TX_COMMON', 'RKI2C_ST', 'SDMMC_HCON', 'USB3_DSTS', 'USB3_GCTL', 'USB3_DCTL', 'CCI500_ERROR_STATUS', 'SDMMC_STATUS', 'EMMCCORE_CLKCTRL', 'DP_TX_VERSION']
                field_exclusions = ['HCON', 'SCALEDOWN', 'ULSTCHNGREQ', 'USBLNKST', 'SCL_ST', 'SDA_ST', 'RESISTOR_CTRL', 'SDCLKFREQSEL', 'DP_TX_VERSION', 'SW_H264ORVP9_ERROR_MODE', 'SW_YUV_CONV_RANGE', 'SW_PP_IN_CRBF_EN', 'WIN1_CSC_MODE', 'WIN0_CSC_MODE', 'WIN0_DATA_FMT', 'CC2_State', 'CC1_State', 'mp_write_format']
                register_exclusions = ['DP_TEST']
                if len(enums) >= 2 and '......' not in field['description'] and field['name'] not in field_exclusions and register['name'] not in register_exclusions:
                    field['description'] = '\n'.join(non_enums)
                    enum_values = []
                    enum_decs = []
                    enum_descriptions = []
                    for i in range(len(enums)):
                        first_colon = enums[i].index(':')
                        value, description = enums[i][:first_colon], enums[i][first_colon+1:]
                        value = value.strip()
                        enum_values.append(value)
                        enum_descriptions.append(description.strip())
                    if all(re.match(r"^[0-9]+'b[01x]+$", value) for value in enum_values):
                        using = 'bin'
                        enum_values = [re.sub(r"^[0-9]+'b", "0b", value) for value in enum_values]
                        enum_decs = [eval(v.replace('x', '1')) for v in enum_values]
                    elif all(re.match(r"^[0-9]+'h[0-9a-fA-F]+$", value) for value in enum_values):
                        using = 'hex'
                        enum_values = [re.sub(r"^[0-9]+'h", "0x", value) for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r"^[01]+$", value) for value in enum_values):
                        using = 'bin'
                        enum_values = [f'0b{value}' for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r'^0x[0-9a-fA-F]+$', value) for value in enum_values):
                        using = 'hex'
                        enum_values = ['0x' + value[2:] for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r"^[01x]+$", value) for value in enum_values):
                        using = 'bin'
                        enum_values = [f'0b{value}' for value in enum_values]
                        enum_decs = [eval(v.replace('x', '1')) for v in enum_values]
                    elif all(re.match(r"^[0-9]+'d[0-9]+$", value) for value in enum_values):
                        using = 'dec'
                        enum_values = [re.sub(r"^[0-9]+'d", "", value) for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r"^[01]+b$", value) for value in enum_values):
                        using = 'bin'
                        enum_values = ['0b' + value[:-1] for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r"^[0-9a-fA-F]+h$", value) for value in enum_values):
                        using = 'hex'
                        enum_values = ['0x' + value[:-1] for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r'^[01]+$', value) for value in enum_values):
                        using = 'bin'
                        enum_values = ['0b' + value for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r'^0b[01]+$', value) for value in enum_values):
                        using = 'bin'
                        enum_values = ['0b' + value[2:] for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    elif all(re.match(r'^[0-9]+$', value) for value in enum_values):
                        using = 'dec'
                        enum_decs = [eval(v) for v in enum_values]
                    elif re.match(r"^[01]+'b$", value):
                        using = 'bin'
                        enum_values = ['0b' + value[:-2] for value in enum_values]
                        enum_decs = [eval(v) for v in enum_values]
                    else:
                        print(register['name'], field['name'], enum_values)
                    # print(enum_descriptions)
                    enum_names = []
                    for enum_value in enum_values:
                        if enum_value.startswith('0b'):
                            enum_names.append('b' + enum_value[2:])
                        elif enum_value.lower().startswith('0x'):
                            enum_names.append('h' + enum_value[2:])
                        else:
                            enum_names.append('d' + enum_value)
                    if len(enum_decs) != len(set(enum_decs)):
                        print('Duplicates', register['name'], field['name'], enum_names)
                    enumerated_values_element = ET.SubElement(field_element, 'enumeratedValues')
                    for i in range(len(enums)):
                        name, value, dec, description = enum_names[i], enum_values[i], enum_decs[i], enum_descriptions[i]
                        end, start = field['bitRange'][1:-1].split(':')[0], field['bitRange'][1:-1].split(':')[-1]
                        start, end = int(start), int(end)
                        max_value = 2 ** (end - start + 1) - 1
                        if dec > max_value:
                            print('Out of range', register['name'], field['name'], value, dec, max_value)
                            continue
                        if description.lower() == 'reserved':
                            continue
                        enumerated_value_element = ET.SubElement(enumerated_values_element, 'enumeratedValue')
                        ET.SubElement(enumerated_value_element, 'name').text = name
                        ET.SubElement(enumerated_value_element, 'value').text = value
                        ET.SubElement(enumerated_value_element, 'description').text = description
                ET.SubElement(field_element, 'description').text = field['description'].replace('\n', '\\n\\n')
                bit_range = field['bitRange']
                if ':' not in bit_range:
                    bit_range = '[' + bit_range[1:-1] + ':' + bit_range[1:-1] + ']'
                ET.SubElement(field_element, 'bitRange').text = bit_range
                ET.SubElement(field_element, 'access').text = field['access']
                # if 'resetValue' in field and field['resetValue'] != 'CALC':
                #     ET.SubElement(field_element, 'resetValue').text = field['resetValue']
                if ('resetValue' not in register or register['resetValue'] == 'CALC') and 'resetValue' in field:
                    bit_range_start = size - int(bit_range.split(':')[0][1:]) - 1
                    bit_range_end = size - int(bit_range.split(':')[1][:-1]) - 1
                    range_reset_value = bin(eval(field['resetValue']))[2:]
                    for j, bit in enumerate(range(bit_range_end, bit_range_start-1, -1)):
                        if j >= len(range_reset_value):
                            break
                        reset_value[bit] = range_reset_value[len(range_reset_value) - 1 - j]
                if 'modifiedWriteValues' in field:
                    ET.SubElement(field_element, 'modifiedWriteValues').text = field['modifiedWriteValues']
                if 'readAction' in field:
                    ET.SubElement(field_element, 'readAction').text = field['readAction']
            if not ('resetValue' in register and register['resetValue'] != 'CALC'):
                reset_value = hex(int(''.join(reset_value), 2))
            ET.SubElement(register_element, 'resetValue').text = reset_value
    if peripheral in interrupts:
        for interrupt in interrupts[peripheral]:
            interrupt_element = ET.SubElement(peripheral_element, 'interrupt')
            ET.SubElement(interrupt_element, 'name').text = interrupt['name'].replace('_intr', '').replace('_int', '').replace('_irq', '')
            ET.SubElement(interrupt_element, 'value').text = str(interrupt['value'])
            ET.SubElement(interrupt_element, 'description').text = 'Interrupt ' + interrupt['name']
tree = ET.ElementTree(root)
dom = xml.dom.minidom.parseString(ET.tostring(root))
pretty_xml = dom.toprettyxml()
with open('RK3399.svd', 'w') as f:
    f.write(pretty_xml)


file = open('peripherals.html', 'w')
file.write('<html><head><title>Peripherals and Fields</title><link rel="stylesheet" href="https://unpkg.com/simpledotcss/simple.min.css"></head><body>')
for peripheral in peripherals:
    file.write(f'<h1>{peripherals[peripheral]["name"]} ({peripherals[peripheral]["groupName"]} Registers)</h1>')
    file.write(f'<p>{peripherals[peripheral]["description"].replace("\n", "<br>")}</p>')
    if 'derivedFrom' in peripherals[peripheral]:
        file.write(f'<p>Derived From: {peripherals[peripheral]["derivedFrom"]}</p>')
        continue
    for register in peripherals[peripheral]['registers']:
        file.write(f'<h2>{register["name"]}</h2>')
        file.write(f'<p>{register["description"].replace("\n", "<br>")}</p>')
        file.write(f'<p>Address Offset: {register["addressOffset"]}</p>')
        file.write(f'<p>Reset Value: {register["resetValue"]}</p>')
        file.write(f'<h3>Fields</h3>')
        file.write('<table>')
        file.write('<tr><th>Field Name</th><th>Bit Range</th><th>Access</th><th>Reset Value</th></tr>')
        for field in register['fields']:
            file.write(f'<tr><td>{field["name"]}</td><td>{field["bitRange"]}</td><td>{field["access"]}</td><td>{field["resetValue"]}</td></tr>')
        file.write('</table>')
file.write('</body></html>')
file.close()


