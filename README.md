# Dynamic Coccyx Angle Measurement Tool

This tool is designed to assist in calculating dynamic coccyx angles from radiographic images as described in the study by Maigne et al. (2000) on coccydynia. The tool allows users to load and overlay radiographic images, rotate and scale them, and measure various angles relevant to coccyx movement, including the coccygeal angle of incidence and the angle of sagittal pelvic rotation, which are key metrics in assessing coccygeal mobility and dysfunction.

## Features
- **Load and Overlay Radiographs**: Import two lateral radiographs (standing and sitting) to compare the coccygeal positions.
- **Image Rotation and Scaling**: Adjust radiograph orientation and size to accurately superimpose images for comparison.
- **Transparency Adjustment**: Control the transparency of the images for clearer comparison.
- **Angle Measurement**: Measure a basic angle
- **Angle A Calculation**: Measure the pelvic rotation (automatic)
- **Angle C Calculation**: Measure the coccyx mobility (manual)
- Not available: measuring coccygeal incidence
  
## Requirements
- Python 3.7+
- PyQt5

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/coccyx-angle-measurement-tool.git
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```bash
    python coccyx_angle_tool.py
    ```
2. Load two radiographs using the `Load Image` buttons. The first image should be a standing lateral radiograph, and the second should be taken in the sitting position, as per the protocol outlined in the article by Maigne et al.
3. Use the provided tools to:
   - Adjust the rotation and transparency of each image.
   - Measure and calculate angles, particularly the coccygeal angle of incidence and the angle of sagittal pelvic rotation.
   - Analyze the differences in coccygeal movement in standing versus sitting radiographs.
4. Angle calculations for determining coccygeal hypermobility and hypomobility

## Coccyx Measurement Protocol

This tool is based on the methodology described in the study "Causes and Mechanisms of Common Coccydynia" (Maigne et al., 2000). The protocol involves:
- Taking radiographs in both standing and sitting positions.
- Measuring the angles of pelvic rotation and coccygeal incidence.
- Identifying coccygeal lesions such as posterior luxation, anterior luxation, hypermobility, and immobile coccyges.

The software allows for the visualization and calculation of these critical angles directly from the radiographs.
