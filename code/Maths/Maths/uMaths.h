#pragma once


#ifdef CREATEDLL_EXPORTS
#define MYMATH_DECLSPEC __declspec(dllexport)
#else
#define MYMATH_DECLSPEC __declspec(dllimport)
#endif


extern "C" {
	MYMATH_DECLSPEC double Sum(double f, double r);
	MYMATH_DECLSPEC double Sub(double f, double r);
	MYMATH_DECLSPEC double Mul(double f, double r);
	MYMATH_DECLSPEC double Div(double f, double r);

	MYMATH_DECLSPEC double map(double x, double in_min, double in_max, double out_min, double out_max);
}