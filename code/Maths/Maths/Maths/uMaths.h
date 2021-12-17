#pragma once


#ifdef CREATEDLL_EXPORTS
#define MYMATH_DECLSPEC __declspec(dllexport)
#else
#define MYMATH_DECLSPEC __declspec(dllimport)
#endif

#define PI 3.141592653589793238462643383279502884197169399375105820974944
#define RAD(a) ((a)*PI/180.)

extern "C" {
	MYMATH_DECLSPEC double Sum(double f, double r);
	MYMATH_DECLSPEC double Sub(double f, double r);
	MYMATH_DECLSPEC double Mul(double f, double r);
	MYMATH_DECLSPEC double Div(double f, double r);

	MYMATH_DECLSPEC double map(double x, double in_min, double in_max, double out_min, double out_max);
	MYMATH_DECLSPEC double Rot_x(double q, double x, double y);
	MYMATH_DECLSPEC double Rot_y(double q, double x, double y);
	MYMATH_DECLSPEC double CAngle(double x, double y);
}