# Automated Exploratory Data Analysis

> All credits to ydata-profiling for building such an amazing tool.

This repo contains the source code for a very minimal [Streamlit](https://streamlit.io) application
that allows users to upload a file and then runs [ydata-profiling](https://github.com/ydataai/ydata-profiling) (formerly 'pandas-profiling')
on the uploaded file and displays the results in a report and provides a download option.

One of the benefits of this is that the interactive app allows you to specify data types of your file
to `ydata-profiling` imporving the results you get.

File sizes are limited by the Streamlit server.

