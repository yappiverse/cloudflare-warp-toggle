MODES = {
    'warp': ('WARP', 'Full tunnel with encrypted DNS'),
    'doh': ('DNS over HTTPS', 'DNS encryption only'),
    'warp+doh': ('WARP + DoH', 'Full tunnel with DoH'),
    'dot': ('DNS over TLS', 'DNS encryption only'),
    'warp+dot': ('WARP + DoT', 'Full tunnel with DoT'),
    'proxy': ('Proxy', 'SOCKS5 proxy tunnel'),
    'tunnel_only': ('Tunnel Only', 'Tunnel without DNS proxy'),
}


MODE_MAP = {
    'warp': 'warp',
    'doh': 'doh',
    'warpwithdnsoverhttps': 'warp+doh',
    'warp+doh': 'warp+doh',
    'dot': 'dot',
    'warpwithdnsovertls': 'warp+dot',
    'warp+dot': 'warp+dot',
    'proxy': 'proxy',
    'tunnel_only': 'tunnel_only',
    'tunnelonly': 'tunnel_only',
}


APP_NAME = "Cloudflare WARP"
WINDOW_WIDTH = 380
WINDOW_HEIGHT = 580
REFRESH_INTERVAL_SECONDS = 3
COMMAND_TIMEOUT = 10
