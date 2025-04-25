import yaml
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import csv
import os
import numpy as np
from scipy.interpolate import splprep, splev

class WaypointEditor:
    def __init__(self, map_image_path, map_yaml_path, waypoints_path):
        self.map_image_path = map_image_path
        self.map_yaml_path = map_yaml_path
        self.waypoints_path = waypoints_path

        self.load_map()
        self.load_waypoints()
        self.setup_plot()

    def load_map(self):
        with open(self.map_yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        self.resolution = yaml_data['resolution']
        self.origin = yaml_data['origin']

        self.img = mpimg.imread(self.map_image_path)
        height, width = self.img.shape[:2]
        self.extent = [
            self.origin[0],
            self.origin[0] + width * self.resolution,
            self.origin[1],
            self.origin[1] + height * self.resolution
        ]

    def load_waypoints(self):
        self.waypoints = []
        if os.path.exists(self.waypoints_path):
            with open(self.waypoints_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    x = float(row['x'])
                    y = float(row['y'])
                    self.waypoints.append((x, y))

    def setup_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig.patch.set_facecolor('white')
        self.ax.imshow(self.img, origin='lower', extent=self.extent)
        self.scatter = None
        self.spline_plot, = self.ax.plot([], [], 'r-', lw=2, label='Interpolated Path')
        self.texts = []
        self.update_plot()

        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.onkeypress)

        self.ax.set_xlabel('X (meters)')
        self.ax.set_ylabel('Y (meters)')
        self.ax.set_title('Waypoint Editor (Left Click=Add, Right Click=Delete, Press "s"=Save)')
        plt.grid(True)
        plt.legend()
        plt.show()

    def update_plot(self):
        if self.scatter is not None and self.scatter.axes is not None:
            self.scatter.remove()
        for txt in self.texts:
            txt.remove()

        if self.waypoints:
            wpx, wpy = zip(*self.waypoints)
            self.scatter = self.ax.plot(wpx, wpy, 'o-', color='cyan')[0]

            self.texts = []
            for idx, (x, y) in enumerate(self.waypoints):
                t = self.ax.text(x, y, str(idx), color='yellow', fontsize=8)
                self.texts.append(t)

            if len(self.waypoints) >= 3:
                self.draw_spline(wpx, wpy)
            else:
                self.spline_plot.set_data([], [])

        self.fig.canvas.draw()

    def onclick(self, event):
        if not event.inaxes:
            return
        if event.button == 1:  # Left click: Add waypoint
            self.waypoints.append((event.xdata, event.ydata))
        elif event.button == 3:  # Right click: Delete closest waypoint
            if self.waypoints:
                closest_idx = self.get_closest_point(event.xdata, event.ydata)
                self.waypoints.pop(closest_idx)
        self.update_plot()

    def onkeypress(self, event):
        if event.key == 's':  # Save to CSV
            self.save_waypoints()

    def get_closest_point(self, x, y):
        distances = [((wx - x)**2 + (wy - y)**2) for wx, wy in self.waypoints]
        return distances.index(min(distances))

    def save_waypoints(self):
        # Save clicked points
        with open(self.waypoints_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['x', 'y'])
            for wp in self.waypoints:
                writer.writerow([wp[0], wp[1]])
        print(f"✅ Clicked waypoints saved to {self.waypoints_path}")

        # Save interpolated spline
        if len(self.waypoints) >= 3:
            smooth_path = os.path.join(os.path.dirname(self.waypoints_path), 'waypoints_smooth.csv')
            self.save_spline(smooth_path)
            print(f"✅ Interpolated waypoints saved to {smooth_path}")
        else:
            print("⚠️ Need at least 3 points for spline interpolation.")

    def draw_spline(self, wpx, wpy):
        if len(wpx) >= 3:
            tck, u = splprep([wpx, wpy], s=0)
            unew = np.linspace(0, 1.0, num=1000)
            out = splev(unew, tck)
            self.spline_plot.set_data(out[0], out[1])
        else:
            self.spline_plot.set_data([], [])

    def save_spline(self, filename):
        if len(self.waypoints) >= 3:
            wpx, wpy = zip(*self.waypoints)
            tck, u = splprep([wpx, wpy], s=0)
            unew = np.linspace(0, 1.0, num=1000)
            out = splev(unew, tck)
            x_smooth, y_smooth = out

            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['x', 'y'])
                for x, y in zip(x_smooth, y_smooth):
                    writer.writerow([x, y])
        else:
            print("⚠️ Not enough points to generate smooth path.")


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.realpath(__file__))
    map_image = os.path.join(base_path, 'Spielberg_map.png')
    map_yaml = os.path.join(base_path, 'Spielberg_map.yaml')
    waypoints_csv = os.path.join(base_path, '..', 'waypoints', 'waypoints.csv')

    editor = WaypointEditor(map_image, map_yaml, waypoints_csv)
