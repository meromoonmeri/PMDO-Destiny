#!/bin/sh

lipo ./build/Release-appletvsimulator/liblua54.framework/liblua54 -verify_arch arm64
if [ $? -eq 0 ]; then
    mv ./build/Release-appletvsimulator/liblua54.framework/liblua54 ./build/Release-appletvsimulator/liblua54.framework/liblua54.old;
    lipo ./build/Release-appletvsimulator/liblua54.framework/liblua54.old -remove arm64 -output ./build/Release-appletvsimulator/liblua54.framework/liblua54;
fi