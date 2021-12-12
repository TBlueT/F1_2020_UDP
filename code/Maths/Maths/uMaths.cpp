#include "pch.h"
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