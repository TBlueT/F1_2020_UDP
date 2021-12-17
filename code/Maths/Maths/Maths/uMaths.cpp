#include "pch.h"
#include <math.h>
#include <cmath>
#include "uMaths.h"


double Sum(double f, double r) {
	return f + r;
}
double Sub(double f, double r) {
	return f - r;
}
double Mul(double f, double r) {
	return f * r;
}
double Div(double f, double r) {
	return f / r;
}

double map(double x, double in_min, double in_max, double out_min, double out_max) {
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

double Rot_x(double q, double x, double y) {
	
	double r = RAD(q);
	double s = sin(r);
	double c = cos(r);

	double xout = c * x - s * y;

	return xout;
}
double Rot_y(double q, double x, double y) {

	double r = RAD(q);
	double s = sin(r);
	double c = cos(r);

	double yout = s * x + c * y;

	return yout;
}
double CAngle(double x, double y) {
	double r = atan2(x, y);
	double d = r * 180 / PI;
	d = (d > 0) ? d : (d + 360);
	return d;
}