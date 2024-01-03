from utils_ import *
import math, copy


class GoBoard:

    def __init__(self, model):
        """
        Constructor method for the GoBoard class.

        Parameters:
        -----------
        model : object
            Object representing the machine learning model associated with the GoBoard.

        Attributes:
        -----------
        model : object
            Machine learning model associated with the GoBoard.

        frame : None
            Placeholder for the current frame (image) processed by the GoBoard.

        results : None
            Placeholder for the detection results obtained from the model.

        tranformed_image : None
            Placeholder for the transformed image, if applicable.

        annotated_frame : None
            Placeholder for the frame with annotations, if applicable.

        state : None
            Placeholder for the current state of the GoBoard.

        """
        self.model = model
        self.frame = None
        self.results = None
        self.tranformed_image = None
        self.annotated_frame = None
        self.state = None
        self.padding = 30
        
        
    def get_state(self):
        """
        Get a deep copy of the current state of the GoBoard.

        Returns:
        -----------
        object
            A deep copy of the current state of the GoBoard.

        """
        return copy.deepcopy(self.state)

    def apply_perspective_transformation(self, double_transform=False):
        if double_transform:
            # Extract corners from the detection results
            input_points = get_corners(self.results, self.padding)

            # Define output points for perspective transformation
            output_edge = 600 + self.padding * 2
            output_points = np.array([[0, 0], [output_edge, 0], [output_edge, output_edge], [0, output_edge]], dtype=np.float32)

            # Perform perspective transformation on the frame
            perspective_matrix = cv2.getPerspectiveTransform(input_points, output_points)
            first_transformed_image = cv2.warpPerspective(self.frame, perspective_matrix, (output_edge, output_edge))
            self.results = self.model(first_transformed_image, verbose=False)
            
        else:
            first_transformed_image = self.frame
        
        self.annotated_frame = self.results[0].plot(labels=False, conf=False)
        # Extract corners from the detection results
        input_points = get_corners(self.results, 0)

        # Define output points for perspective transformation
        output_edge = 600
        output_points = np.array([[0, 0], [output_edge, 0], [output_edge, output_edge], [0, output_edge]], dtype=np.float32)

        # Perform perspective transformation on the frame
        self.perspective_matrix = cv2.getPerspectiveTransform(input_points, output_points)
        self.transformed_image = cv2.warpPerspective(first_transformed_image, self.perspective_matrix, (output_edge, output_edge))
    
    def assign_stones(self, white_stones_transf, black_stones_transf, transformed_intersections):
        """
        Assign stones to intersections based on their proximity.

        Parameters:
        -----------
        white_stones_transf : numpy.ndarray
            Transformed coordinates of white stones.

        black_stones_transf : numpy.ndarray
            Transformed coordinates of black stones.

        transformed_intersections : numpy.ndarray
            Transformed coordinates of intersections.

        """ 

        self.map = map_intersections(transformed_intersections)
        self.state = np.zeros((19, 19, 2))
        
        for stone in white_stones_transf:
            
            # Draw the position of the stone for testing 
            cv2.circle(self.transformed_image, np.array(stone).astype(dtype=np.int32), 3, (0, 0, 255), 2)
            
            nearest_corner = self.find_nearest_corner(transformed_intersections, stone)
            self.state[self.map[nearest_corner][1], self.map[nearest_corner][0], 1] = 1

            # Draw the distance between the center of the stones and the intersection it was assigned to for testing
            cv2.line(self.transformed_image, (int(stone[0]), int(stone[1])), nearest_corner, (0, 255, 255), 2)
            
                
        for stone in black_stones_transf:
            
            # Draw the position of the stone for testing 
            cv2.circle(self.transformed_image, np.array(stone).astype(dtype=np.int32), 3, (0, 0, 255), 2)
            
            nearest_corner = self.find_nearest_corner(transformed_intersections, stone)
            self.state[self.map[nearest_corner][1], self.map[nearest_corner][0], 0] = 1
            
            # Draw the distance between the center of the stones and the intersection it was assigned to for testing
            cv2.line(self.transformed_image, (int(stone[0]), int(stone[1])), nearest_corner, (0, 255, 255), 2)
        
        # imshow_(self.transformed_image)
    
    def find_nearest_corner(self, transformed_intersections, stone):
        """
        Find the nearest corner point from a list of transformed intersections to a given stone.

        This function calculates the distance between the stone and each transformed intersection point,
        and returns the coordinates of the nearest corner point along with the distance.

        Args:
            transformed_intersections (list): List of transformed intersection points.
            stone (tuple): Coordinates of the stone.

        Returns:
            tuple: Coordinates of the nearest corner point.
        """
        nearest_corner = None
        closest_distance = float('inf')  # Set initial distance to positive infinity

        # Iterate through transformed intersections to find the nearest corner
        for inter in transformed_intersections:
            distance = math.dist(inter, stone)
            if distance < closest_distance:
                nearest_corner = tuple(inter)
                closest_distance = distance

        return nearest_corner

    def process_frame(self, frame):
        """
        Process a frame to extract information about the Go board.

        Parameters:
        -----------
        frame : numpy.ndarray
            Input frame representing the Go board.

        """
        # Store the current frame
        self.frame = frame

        # Obtain detection results from the model
        self.results = self.model(self.frame, verbose=False)

        self.apply_perspective_transformation(double_transform=True)
        
        # Annotate the frame with detection results (without labels and confidence)
        self.annotated_frame = self.results[0].plot(labels=False, conf=False)
        
        # Detect vertical and horizontal lines
        vertical_lines, horizontal_lines = lines_detection(self.results, self.perspective_matrix)

        # Remove duplicate lines
        vertical_lines = removeDuplicates(vertical_lines)
        horizontal_lines = removeDuplicates(horizontal_lines)

        # Restore and remove lines
        vertical_lines = restore_and_remove_lines(vertical_lines)
        horizontal_lines = restore_and_remove_lines(horizontal_lines)

        # Add missing lines at the edges
        vertical_lines = add_lines_in_the_edges(vertical_lines, "vertical")
        horizontal_lines = add_lines_in_the_edges(horizontal_lines, "horizontal")

        # Remove duplicate lines again
        vertical_lines = removeDuplicates(vertical_lines)
        horizontal_lines = removeDuplicates(horizontal_lines)

        # Get key points for black and white stones
        black_stones = get_key_points(self.results, 0, self.perspective_matrix)
        white_stones = get_key_points(self.results, 6, self.perspective_matrix)

        # Extract clusters of lines within the valid image region
        cluster_1 = vertical_lines[(vertical_lines <= 600).all(axis=1) & (vertical_lines >= 0).all(axis=1)]
        cluster_2 = horizontal_lines[(horizontal_lines <= 600).all(axis=1) & (horizontal_lines >= 0).all(axis=1)]

        # Check if the correct number of lines is detected
        if len(cluster_1) != 19 or len(cluster_2) != 19:
            raise Exception(f"Incorrect number of lines was detected: {len(cluster_1)} vertical lines and {len(cluster_2)} horizontal lines")

        # Detect intersections between vertical and horizontal lines
        intersections = detect_intersections(cluster_1, cluster_2, self.transformed_image)

        # Check if any intersections were found
        if len(intersections) == 0:
            raise Exception("No intersections were found!")
        if len(intersections) != 361:
            print("Not all intersections were found!")

        # Assign stones to intersections
        self.assign_stones(white_stones, black_stones, intersections)