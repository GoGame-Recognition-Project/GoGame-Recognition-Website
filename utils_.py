import cv2
import numpy as np
from sklearn.cluster import KMeans, DBSCAN


def line_equation(x1, y1, x2, y2):
    """
    Calculate the slope and the intercept b in the line equation y = slope * x + b

    Args:
    -----------
    x1: float
        The start point of the line in X direction
    y1: float
        The start point of the line in Y direction
    x2: float
        The end point of the line in X direction
    y2: float
        The end point of the line in Y direction
    
    Returns:
    --------
    float
        slope of the line
    float 
        intercept of the line 
    """
    if x1 == x2:
        "if slope is infinite , y = x1 = c"
        slope = float('Inf')
        b = x1
    else:
        slope = (y2-y1) / (x2-x1)
        b = y1 - slope * x1
    return slope, b

def adress_lines(lines):
    """
    Sort the order of endpoints

    Args:
    -----------
    lines: list
        list of lines unsorted
    
    Returns:
    --------
    list
        sorted lines    
    """
    for i in range(len(lines)):
        x1, y1, x2, y2 = lines[i]
        if (x1 + y1) > (x2 + y2):
            x1, x2, y1, y2 = x2, x1, y2, y1
            lines[i] = x1, y1, x2, y2
    return lines

def are_similar(line1, line2, threshold=10):
    """
    Compare two lines and decide if they're almost the same line based on a certain threshold

    Args:
    -----------
    line1: numpy.ndarray
        4 elements array representing the first line [x1, y1, x2, y2]
    line2: numpy.ndarray
        4 elements array representing the second line [x1, y1, x2, y2]
    threshold: int
        Smallest the difference between 2 lines (default is 10)
    
    Returns:
    --------
    bool
        true if similar, else false    
    """
    return np.all(np.abs(line1 - line2) <= threshold)


# def removeDuplicates(lines):
#     """
#     Group similar lines and take the average of each group to keep one line per group

#     Args:
#     -----------
#     lines: list
#         list of lines to be filtered
    
#     Returns:
#     --------
#     numpy.ndarray
#         filtered list of lines   
#     """
#     grouped_lines = {}
#     for line in lines:
#         x1, y1, x2, y2 = line
#         found = False
#         for key in grouped_lines.keys():
#             for element in grouped_lines[key]:
#                 if are_similar(element, line, threshold=15):
#                     grouped_lines[key] = grouped_lines[key] + [line]
#                     found = True
#                     break
#         if not found:
#             grouped_lines[(x1, y1, x2, y2)] = [line]

#     final_lines2 = []
#     second_dict = {}
#     for key in grouped_lines.keys():
#         mean_line = np.mean(grouped_lines[key], axis=0).astype(dtype=int)
#         final_lines2.append(mean_line)
#         second_dict[tuple(mean_line)] = [mean_line]
    
#     for line in lines:
#         x1, y1, x2, y2 = line
#         found = False
#         for key in second_dict.keys():
#             if are_similar(key, line, threshold=5):
#                 second_dict[key] = second_dict[key] + [line]
#                 found = True
#                 break
            
#     final_lines = []
#     for key in second_dict.keys():
#         mean_line = np.mean(second_dict[key], axis=0).astype(dtype=int)
#         final_lines.append(mean_line)
    
#     return np.array(final_lines).astype(np.int32)

def removeDuplicates(lines):
    grouped_lines = {}
    for line in lines:
        x1, y1, x2, y2 = line
        found = False
        for key in grouped_lines.keys():
            if are_similar(key, line):
                grouped_lines[key] = grouped_lines[key] + [line]
                found = True
                break
        if not found:
            grouped_lines[(x1, y1, x2, y2)] = [line]

    final_lines = []
    for key in grouped_lines.keys():
        final_lines.append(np.mean(grouped_lines[key], axis=0))
    
    return np.array(final_lines).astype(int)


def is_vertical(x1, y1, x2, y2):
    """
    Decide if a line is vertical or not

    Args:
    -----------
    x1: float
        The start point of the line in X direction
    y1: float
        The start point of the line in Y direction
    x2: float
        The end point of the line in X direction
    y2: float
        The end point of the line in Y direction
    
    Returns:
    --------
    bool
        true if vertical, else false    
    """
    return abs(x1 - x2) < 50 and abs(y1 - y2) > 50

def intersect(line1, line2):
    """
    Find the intersection of 2 lines

    Args:
    -----------
    line1: list
        list of start point x, start point y, end point x, end point y
    line2: list
        list of start point x, start point y, end point x, end point y

    Returns:
    --------
    numpy.ndarray
        x and y coordinates of the intersection    
    """
    slope1, b1 = line_equation(*line1)
    slope2, b2 = line_equation(*line2)
    if slope1 == float('Inf'):
        x = b1
        y = slope2 * x + b2
    elif slope2 == float('Inf'):
        x = b2
        y = slope1 * x + b1
    else:
        x = (b2 - b1) / (slope1 - slope2)
        y = slope1 * x + b1
    return np.array([int(np.round(x)), int(np.round(y))])


def map_intersections(intersections, board_size=19):
    """
    Set up the board with 19x19=361 intersections 

    Args:
    -----------
    intersections: numpy.ndarray
        List of found and interpolated intersections
    board_size:
        Size of the board (default is 19x19)

    Returns:
    --------
    dict
        The board, in which each key correponds to an intersection and its value represents its coordinate on the board
        
    """

    sorted_indices = np.lexsort((intersections[:, 0], intersections[:, 1]))
    cleaned_intersections = intersections[sorted_indices]
    cleaned_intersections = cleaned_intersections.tolist()
    
    board = {}
    for j in range(0, board_size):
        row = cleaned_intersections[:board_size]
        cleaned_intersections = cleaned_intersections[board_size:]
        row.sort(key=lambda x: x[0])
        for i in range(board_size):
            if len(row) != 0:
                board[tuple(row.pop(0))] = (i, j)
    
    return board

def detect_intersections(cluster_1, cluster_2, image):
    """
    Detect intersections between vertical and horizontal line clusters.

    Args:
    -----------
    cluster_1 : numpy.ndarray
                Array of vertical lines represented by coordinates [x1, y1, x2, y2].
    cluster_2 : numpy.ndarray
                Array of horizontal lines represented by coordinates [x1, y1, x2, y2].
    image : numpy.ndarray
            Image array to define the boundary for intersection points.

    Returns:
    --------
    numpy.ndarray
        Array of intersection points between vertical and horizontal line clusters.
    """
    intersections = []
    
    for v_line in cluster_1:
        for h_line in cluster_2:
            inter = intersect(v_line, h_line)
            
            if all(image.shape[:1] > inter) and all(inter >= 0):
                intersections.append(tuple(inter.astype(dtype=int)))
    
    return np.array(intersections)


def calculate_distances(lines):
    """
    Calculate distances between consecutive lines.

    Args:
    -----------
    lines : numpy.ndarray
            Array of lines represented by coordinates [x1, y1, x2, y2].

    Returns:
    --------
    list : numpy.ndarray
            List of distances between consecutive lines.
    """
    distances = [(np.linalg.norm(lines[i + 1][:2]-lines[i][:2]) + np.linalg.norm(lines[i + 1][2:]-lines[i][2:])) / 2 for i in range(len(lines) - 1)]
    return distances

def find_common_distance(distances, target_distance=30):
    """
    Find the common distance among a set of distances using DBSCAN clustering.

    Args:
    -----------
    distances : list
                List of distances to be clustered and analyzed.
    target_distance : float, optional
                      The target distance to find among the clusters (default=30).

    Returns:
    --------
    Tuple
        Tuple containing the mean of the distances in the cluster with the target distance
        and the distances in that cluster.
    """
    
    # Reshape distances into a column vector
    distances_ = np.array(distances).reshape((-1, 1))

    # Apply DBSCAN clustering
    dbscan = DBSCAN(eps=1, min_samples=1)
    labels = dbscan.fit_predict(distances_)
    
    means = np.array([])
    unique_labels = np.unique(labels)
    label_index = np.array([])
    
    # Calculate means for each cluster and store label and mean in arrays
    for label in unique_labels:
        means = np.append(means, np.mean(distances_[labels==label]))
        label_index = np.append(label_index, label)

    # Find the index of the cluster with the closest mean to the target distance
    index = np.argmin(np.abs(means - target_distance))
    
    # Return the mean of distances in the chosen cluster and the distances in that cluster
    return means[index], distances_[labels==label_index[index]]

def is_approx_multiple(value, base, threshold):
    """
    Check if a value is approximately a multiple of a given base within a specified threshold.

    Args:
    -----------
    value : float
            The value to check.
    base : float
           The base value for which the check is performed.
    threshold : float
                The maximum allowed deviation from being a multiple.

    Returns:
    --------
    bool
        True if the value is approximately a multiple of the base within the threshold, False otherwise.
    """
    if value < base:
        return (base - value) < threshold
    return abs((value%base) - base) < threshold or abs(value%base) < threshold

    # return abs(value - math.floor(value / base) * base) < threshold

def restore_and_remove_lines(lines, distance_threshold=10):
    """
    Restore missing lines in a set of line segments based on a common spacing,
    and remove lines that do not conform to the common spacing.

    Args:
    -----------
    lines : numpy.ndarray
        An array representing line segments. Each row should contain four elements: [x1, y1, x2, y2].

    distance_threshold : float, optional (default=10)
        The maximum allowed deviation from the common spacing when identifying missing lines.

    Returns:
    --------
    numpy.ndarray
        An array representing the lines with missing segments restored and non-conforming lines removed.

    Notes:
    ------
    The function assumes that the input lines are sorted based on the y-axis (vertical lines) or x-axis (horizontal lines).

    The common spacing is calculated based on the mean distance between consecutive lines.
    Missing lines are added to bridge the gaps, and lines that deviate from the common spacing are removed.

    The function supports both horizontal and vertical lines.

    """
    
    # ax=0 : x axis / ax=1 : y axis
    lines = np.sort(lines, axis=0)
    
    # Calculate distances between consecutive lines
    distances = calculate_distances(lines)
    
    # If there are only one or fewer lines, no restoration is needed
    if len(distances) <= 1:
        return lines
    
    # Find the common distance and update the distances array
    mean_distance, distances = find_common_distance(distances)
    
    restored_lines = []
    
    i = 0
    while i < len(lines) - 1:
        # Calculate spacing between consecutive lines
        spacing = (np.linalg.norm(lines[i + 1][:2]-lines[i][:2]) + np.linalg.norm(lines[i + 1][2:]-lines[i][2:]))/2
        
        # Check if spacing is approximately a multiple of the mean distance
        if is_approx_multiple(spacing, mean_distance, distance_threshold):
            # If spacing is greater than or equal to the mean distance, restore missing lines
            if spacing >= mean_distance:
                num_missing_lines = round(spacing / mean_distance) - 1
                for j in range(1, num_missing_lines + 1):
                    if is_vertical(*lines[i]):
                        x1 = lines[i][0] + j * mean_distance
                        y1 = lines[i][1]
                        x2 = lines[i][2] + j * mean_distance
                        y2 = lines[i][3]
                    else:
                        x1 = lines[i][0]
                        y1 = lines[i][1] + j * mean_distance
                        x2 = lines[i][2]
                        y2 = lines[i][3] + j * mean_distance
                    restored_lines.append([x1, y1, x2, y2])
        else:
            # If spacing is not a multiple, remove the next line
            lines = np.delete(lines, i+1, axis=0)
            i -= 1
        i += 1
  
    # Append the restored lines to the original array
    if len(restored_lines) != 0:
        lines = np.append(lines, np.array(restored_lines, dtype=int), axis=0)
    
    lines = np.sort(lines, axis=0)
    
    return lines


def non_max_suppression(boxes, overlapThresh=0.5):
    """
    Apply non-maximum suppression to eliminate redundant bounding boxes.

    Args:
    -----------
    boxes : numpy.ndarray
            Array of bounding boxes with coordinates [x1, y1, x2, y2].
    overlapThresh : float, optional
                    Threshold for overlap to consider bounding boxes as redundant (default=0.5).

    Returns:
    --------
    numpy.ndarray
        Array of picked bounding boxes after non-maximum suppression.
    """
    
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []
    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")
    # initialize the list of picked indexes	
    pick = []
    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]
        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlapThresh)[0])))
    # return only the bounding boxes that were picked using the
    # integer data type
    return boxes[pick].astype("int")



def lines_detection(model_results, perspective_matrix):
    """
    Process model results to identify and cluster all intersections.

    Args:
    -----------
    model_results : numpy.ndarray
                    List of model results containing information about boxes.
    perspective_matrix : numpy.ndarray
                    Perspective transformation matrix
    
    Returns:
    --------
    Tuple of two numpy.ndarrays representing clustered vertical and horizontal lines.
    """
    empty_intersections = get_key_points(model_results, 3, perspective_matrix)
    empty_corner = get_key_points(model_results, 4, perspective_matrix)
    empty_edge = get_key_points(model_results, 5, perspective_matrix)

    arrays = [empty_intersections, empty_corner, empty_edge]

    arrays = [arr for arr in arrays if arr.size > 0]

    all_intersections = np.concatenate(arrays, axis=0)

    all_intersections = all_intersections[all_intersections[:, 0].argsort()]
    all_intersections_x = all_intersections[:,0].reshape((-1, 1))

    kmeans = KMeans(n_clusters=19, n_init=10)
    kmeans.fit(all_intersections_x)

    # Get the cluster labels for each line
    cluster_labels = kmeans.labels_
    unique_labels, label_counts = np.unique(cluster_labels, return_counts=True)

    # Sort the labels based on their counts in decreasing order
    sorted_indices = np.argsort(label_counts)[::-1]
    sorted_unique_labels = unique_labels[sorted_indices]


    lines_equations = np.array([]).reshape((-1, 2))
    lines_points_length = np.array([])
    cluster_vertical = np.array([]).reshape((-1, 4))

    for label in sorted_unique_labels:
        line = all_intersections[cluster_labels==label]
        if len(line) > 2:
            slope, intercept = np.polyfit(line[:,1], line[:,0], 1) # on inverse x et y
            line_ = np.array([intercept, 0, slope * 600 + intercept, 600])# on iverse les x et y
            lines_equations = np.append(lines_equations, [[slope, intercept]], axis=0)
        else:
            if len(cluster_vertical) == 0:
                raise Exception(f"[BoardDetectionException]: Unable to reconstruct all vertical lines")
            elif len(line) < 1:
                raise Exception(f"[BoardDetectionException]: Unable to reconstruct vertical line at point {line}")
            else:
                x1, y1 = line[0]
                slope = np.average(lines_equations[:,0], weights=lines_points_length, axis=0)
                intercept = x1 - slope * y1
                line_ = np.array([intercept, 0, slope * 600 + intercept, 600])
                lines_equations = np.append(lines_equations, [[slope, intercept]], axis=0)
        lines_points_length = np.append(lines_points_length, [len(line)], axis=0)

        cluster_vertical = np.append(cluster_vertical, [line_], axis=0)
    
    cluster_vertical = adress_lines(cluster_vertical)
    cluster_vertical = np.sort(cluster_vertical, axis=0).astype(int)


    all_intersections = all_intersections[all_intersections[:, 1].argsort()]
    all_intersections_y = all_intersections[:,1].reshape((-1, 1))

    kmeans = KMeans(n_clusters=19, n_init=10)
    kmeans.fit(all_intersections_y)

    # Get the cluster labels for each line
    cluster_labels = kmeans.labels_
    unique_labels, label_counts = np.unique(cluster_labels, return_counts=True)

    # Sort the labels based on their counts in decreasing order
    sorted_indices = np.argsort(label_counts)[::-1]
    sorted_unique_labels = unique_labels[sorted_indices]

    # img = np.copy(transformed_image)
    lines_equations = np.array([]).reshape((-1, 2))
    lines_points_length = np.array([])
    cluster_horizontal = np.array([]).reshape((-1, 4))

    for label in sorted_unique_labels:
        line = all_intersections[cluster_labels==label]
        
        if len(line) > 2:
            line = line[np.argsort(line[:, 0])]
            slope, intercept = np.polyfit(line[:,0], line[:,1], 1)
            line = np.array([0, intercept, 600, slope * 600 + intercept])
            lines_equations = np.append(lines_equations, [[slope, intercept]], axis=0)
        else:
            if len(cluster_horizontal) == 0:
                raise Exception(f"BoardDetectionException: Unable to reconstruct ALL HORIZONTAL LINES")
            elif len(line) < 1:
                raise Exception(f"BoardDetectionException: Unable to reconstruct line at point {line}")
            else:
                x1, y1 = line[0]
                slope = np.average(lines_equations[:,0], weights=lines_points_length, axis=0)
                intercept = y1 - slope * x1
                line = np.array([0, intercept, 600, slope * 600 + intercept])
                lines_equations = np.append(lines_equations, [[slope, intercept]], axis=0)
        lines_points_length = np.append(lines_points_length, [len(line)], axis=0)

        cluster_horizontal = np.append(cluster_horizontal, [line], axis=0)
    
    cluster_horizontal = adress_lines(cluster_horizontal)
    cluster_horizontal = np.sort(cluster_horizontal, axis=0).astype(int)
 
    return np.array(cluster_vertical).reshape((-1, 4)), np.array(cluster_horizontal).reshape((-1, 4))
    
def get_corners_inside_box(corners_boxes, board_box):
    """
    Check if any corner of a set of boxes is inside another bounding box.

    Args:
    -----------
    corners_boxes : numpy.ndarray
        An array representing corners of boxes. Each row should contain four elements: [x1, y1, x2, y2].

    board_box : tuple
        A tuple representing the bounding box coordinates (x1, y1, x2, y2) to check against.

    Returns:
    --------
    numpy.ndarray
        An array containing corners that are inside the specified bounding box.

    """
        
    x1, y1, x2, y2 = board_box

    # Extract the coordinates of the squares
    square_x1 = corners_boxes[:, 0]
    square_y1 = corners_boxes[:, 1]
    square_x2 = corners_boxes[:, 2]
    square_y2 = corners_boxes[:, 3]

    # Check if any corner of the corners_boxes is inside the board_box
    condition = (
        ((square_x1 >= x1) & (square_x1 <= x2) & (square_y1 >= y1) & (square_y1 <= y2)) |
        ((square_x2 >= x1) & (square_x2 <= x2) & (square_y1 >= y1) & (square_y1 <= y2)) |
        ((square_x1 >= x1) & (square_x1 <= x2) & (square_y2 >= y1) & (square_y2 <= y2)) |
        ((square_x2 >= x1) & (square_x2 <= x2) & (square_y2 >= y1) & (square_y2 <= y2))
    )

    # Select corners_boxes that meet the condition
    return corners_boxes[condition]
        
def get_corners(results, padding=None):
    """
    Extract and arrange four corners from object detection results.

    Args:
    -----------
    results : list
        A list containing object detection results.

    Returns:
    --------
    numpy.ndarray
        An array containing four corners of the board arranged in a specific order.

    Raises:
    -------
    Exception
        Raised when an incorrect number of corners is detected.

    Notes:
    ------
    The function extracts corners from the object detection results.
    It then performs non-maximum suppression to remove redundant corners, ensuring only distinct corners are considered.
    The corners are further filtered to only include those inside the board box.
    Finally, the four corners are arranged in a specific order to form a coherent representation.

    """
    
    corner_boxes = np.array(results[0].boxes.xyxy[results[0].boxes.cls == 2])
    
    if len(corner_boxes) < 4:
        raise Exception(f"[BoardDetectionException]: Incorrect number of corners! Detected {len(corner_boxes)} corners")


    corner_boxes_ = non_max_suppression(corner_boxes)

    model_board_edges = results[0].boxes.xyxy[results[0].boxes.cls == 1][0]
    
    corner_boxes = get_corners_inside_box(corner_boxes_, np.array(model_board_edges))

    if len(corner_boxes) != 4:
        raise Exception(f"[BoardDetectionException]: Incorrect number of corners! Detected {len(corner_boxes)} corners and {len(corner_boxes_)} corners with NMS")

    corner_centers = ((corner_boxes[:,[0, 1]] + corner_boxes[:,[2, 3]])/2)
    
    corner_centers = corner_centers[corner_centers[:, 1].argsort()]
    
    upper = corner_centers[:2]
    lower = corner_centers[2:]
    
    upper = upper[upper[:, 0].argsort()]
    lower = lower[lower[:, 0].argsort()[::-1]]
    
    corner_centers = np.concatenate((upper, lower)).astype(dtype=np.float32)
    
    if not padding is None:
        corner_centers[0] += np.array([-padding, -padding])
        corner_centers[1] += np.array([padding, -padding])
        corner_centers[2] += np.array([padding, padding])
        corner_centers[3] += np.array([-padding, padding])
    
    return corner_centers

def get_key_points(results, class_, perspective_matrix, output_edge=600):
    """
    Extract and transform key points from object detection results.

    Parameters:
    -----------
    results : object
        Object containing detection results, typically from an object detection model.

    class_ : int
        Class index for the desired key points.

    perspective_matrix : numpy.ndarray
        Perspective transformation matrix used to transform key points.

    output_edge : int, optional
        Maximum value for the transformed key points' coordinates. Default is 600.

    Returns:
    -----------
    numpy.ndarray
        Transformed key points within the specified output edge.

    """
    # Extract raw key points from the detection results for the specified class
    key_points = results[0].boxes.xywh[results[0].boxes.cls == class_].reshape((-1, 4))
    

    if not key_points is None:
        if len(key_points) != 0:
            key_points = np.array(key_points[:, [0, 1]])
            key_points_transf = cv2.perspectiveTransform(key_points.reshape((1, -1, 2)), perspective_matrix).reshape((-1, 2))
            return key_points_transf[(key_points_transf[:, 0:2] >= 0).all(axis=1) & (key_points_transf[:, 0:2] <= output_edge).all(axis=1)]

    return np.array(key_points)


def add_lines_in_the_edges(lines, type):
    """
    Add missing lines at the edges based on the specified line type.

    Parameters:
    -----------
    lines : numpy.ndarray
        Array of lines represented by their endpoints.

    type : str
        Type of lines to be added ('vertical' or 'horizontal').

    Returns:
    -----------
    numpy.ndarray
        Array of lines with potentially added lines at the edges.

    """
    mean_distance = average_distance(lines)
    # print(mean_distance)

    if len(lines) != 18 and len(lines) != 17:
        return lines
    
    appended = False
    if type == "vertical":
        # 600 being the image size
        left_border =  np.array([0, 0, 0, 600])
        right_border = np.array([600, 0, 600, 600])
        if line_distance(lines[0], left_border) > mean_distance:
            x1 = lines[0][0]-mean_distance
            y1 = lines[0][1]
            x2 = lines[0][2]-mean_distance
            y2 = lines[0][3]
            lines = np.append(lines, [[x1, y1, x2, y2]], axis=0)
            appended = True
        if line_distance(lines[-1], right_border) > mean_distance:
            x1 = lines[-1][0]+mean_distance
            y1 = lines[-1][1]
            x2 = lines[-1][2]+mean_distance
            y2 = lines[-1][3]  
            lines = np.append(lines, [[x1, y1, x2, y2]], axis=0)
            appended = True
        lines = lines[lines[:, 0].argsort()]
            
        if not appended:
            print("No missing edges in the vertical lines")


    elif type == "horizontal":
        # 600 being the image size
        
        top_border =  np.array([0, 0, 600, 0])
        bottom_border = np.array([0, 600, 600, 600])
        if line_distance(lines[0], top_border) > mean_distance:
            x1 = lines[0][0]
            y1 = lines[0][1]-mean_distance
            x2 = lines[0][2]
            y2 = lines[0][3]-mean_distance
            lines = np.append(lines, [[x1, y1, x2, y2]], axis=0)
            appended = True
        if line_distance(lines[-1], bottom_border) > mean_distance:
            x1 = lines[-1][0]
            y1 = lines[-1][1]+mean_distance
            x2 = lines[-1][2]
            y2 = lines[-1][3]+mean_distance   
            lines = np.append(lines, [[x1, y1, x2, y2]], axis=0)              
            appended = True
        
        lines = lines[lines[:, 1].argsort()]
            
        if not appended:
            print("No missing edges in the horizontal lines")
    else:
        print("Please specify a line type")
    

    return lines.astype(int)
    
    
def line_distance(line1, line2):
    """
    Calculate the average Euclidean distance between two lines.

    Parameters:
    -----------
    line1 : numpy.ndarray
        Array representing the endpoints of the first line.

    line2 : numpy.ndarray
        Array representing the endpoints of the second line.

    Returns:
    -----------
    float
        Average Euclidean distance between the two lines.

    """
    return (np.linalg.norm(line1[:2]-line2[:2]) + np.linalg.norm(line1[2:]-line2[2:])) / 2


# def calculate_distances(lines):
#     """
#     Calculate the distances between consecutive pairs of lines.

#     Parameters:
#     -----------
#     lines : list
#         List of arrays, each representing the endpoints of a line segment.

#     Returns:
#     -----------
#     list
#         List of distances between consecutive pairs of lines.

#     """
#     return [line_distance(lines[i + 1], lines[i]) for i in range(len(lines) - 1)]

def average_distance(lines):
    """
    Calculate the average distance between consecutive pairs of lines.

    Parameters:
    -----------
    lines : list
        List of arrays, each representing the endpoints of a line segment.

    Returns:
    -----------
    float
        Average distance between consecutive pairs of lines.

    """
    distances = [line_distance(lines[i + 1], lines[i]) for i in range(len(lines) - 1)]
    mean_distance = np.average(distances)
    return mean_distance
