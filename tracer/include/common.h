#ifndef _COMMON_HPP
#define _COMMON_HPP

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>

#ifdef CONFIG_DEBUG
#define DEBUG(...) do{ fprintf( stderr, __VA_ARGS__ ); } while( 0)
#else
#define DEBUG(...) do{ } while ( 0 )
#endif

#define fail(...) \
{\
    fprintf(stderr, "[ERROR][%s:%d:%s]: %s", \
            __FILE__, __LINE__, __func__, strerror(errno)); \
    fprintf(stderr, __VA_ARGS__); \
    exit(-1); \
}

#define T_INFO(...) \
{\
    fprintf(stderr, "[INFO][%s:%d:%s]: ", \
            __FILE__, __func__, __LINE__); \
    fprintf(stderr, __VA_ARGS__); \
}

#define T_WARN(...) \
{\
    fprintf(stderr, "[WARN][%s:%d:%s]: ", \
            __FILE__, , __LINE__, __func__); \
    fprintf(stderr, __VA_ARGS__); \
}

#define T_DEBUG(...) \
{\
    fprintf(stderr, "[DEBUG][%s:%d|%s]: ", __FILE__, __LINE__, __func__); \
    fprintf(stderr, __VA_ARGS__); \
}

#define T_ERROR(...) \
{\
    fprintf(stderr, "[ERROR][%s:%s|%s]:", \
            __FILE__, __LINE__, __func__); \
    fprintf(stderr, __VA_ARGS__); \
}

#endif
