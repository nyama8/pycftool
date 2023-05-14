import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np

from IPython.display import display

from pycftool_Backend import *
from pycftool_Fit import *
from pycftool_FitModel import *

class Frontend():

    def __init__(self, backend):

        self.backend = backend


        # Generate the figure output widget
        # Plot the initial data and configure the display settings
        self.output = widgets.Output(label=None)

        with self.output:
            self.fig, self.ax = plt.subplots(constrained_layout=True, figsize=(6, 4))

        self.line, = self.ax.plot(self.backend.x, self.backend.y, 'k')
        self.fig.canvas.toolbar_position = 'bottom'
        self.ax.grid(True)

        # list of all plt.line objects for future generated fits
        self.fit_curve_lines = []
        # Line object for the current fit line
        self.current_fit_line, = self.ax.plot([])


        # High-level control box
        self.ctrl_b1 = widgets.Button(description='Fit data in range')
        self.ctrl_b2 = widgets.Button(description='Cancel', disabled=True)

        self.ctrl_box = widgets.VBox(
            [
                #widgets.HTML(
                #                value='<b>Control</b>',
                #                description=''
                #            ),
                widgets.Label('Control box'),
                self.ctrl_b1,
                self.ctrl_b2
            ]
        )


        # Control box widget observe and update
        self.ctrl_b1.on_click(self.__goto_FitMode)
        self.ctrl_b2.on_click(self.__goto_SearchMode)



        # Fit control box
        self.backend.cur_fitmodel = self.backend.fit_models[0]

        self.fitmodel_dropdown = widgets.Dropdown(value=self.backend.model_names[0],
                                             options=self.backend.model_names,
                                             description='Fit Model',
                                             disabled=True
                                            )
        # Watch the dropdown
        self.fitmodel_dropdown.observe(self.__init_FitModel, 'value')


        # For each parameter, generate an input floattext widget
        # Create an observer and write the parameter values to the backend
        self.param_input_widgets = []
        self.backend.param_vect = []

        for k in range(self.backend.cur_fitmodel.num_params):

            # Create the new input text widgets
            self.param_input_widgets.append(
                widgets.FloatText(value=self.backend.cur_fitmodel.param_default[k],
                                  description=self.backend.cur_fitmodel.param_names[k],
                                  continuous_update=False,
                                  disabled=True
                                 )
            )

            # Construct the parameter backend values
            self.backend.param_vect.append(self.backend.cur_fitmodel.param_default[k])


            # Observe the input widgets
            self.param_input_widgets[k].observe(self.backend.update_param, 'value')


        # Make the box of parameter input widgets
        self.param_box = widgets.VBox(
            self.param_input_widgets
        )

        # Join the dropdown and fit parameter widgets
        self.fit_box = widgets.VBox([self.fitmodel_dropdown, self.param_box])

        # Fit results widget box
        self.trigger_fit_button = widgets.Button(description='Run fit', disabled=True)

        # Attempt to fit when triggered
        self.trigger_fit_button.on_click(self.backend.fit_data)

        # Create a set of output text widgets to display the results
        self.param_output_widgets = []
        for k in range(self.backend.cur_fitmodel.num_params):

            self.param_output_widgets.append(
                widgets.FloatText(value=None,
                                  description=self.backend.cur_fitmodel.param_names[k],
                                  continuous_update=False,
                                  disabled=True
                                 )
            )




        # Button to accept the fit
        self.accept_fit_button = widgets.Button(description='Accept fit', disabled=True)

        # When triggered accept the fit and return to search mode
        self.accept_fit_button.on_click(self.__accept_fit)


        self.output_box = widgets.VBox(
            [self.trigger_fit_button, self.accept_fit_button] + self.param_output_widgets
        )


        # Widgets to save the fits
        self.save_results_button = widgets.Button(description='Save fits')
        self.save_results_button.on_click(self.backend.save)

        self.save_box = widgets.VBox( [widgets.Label('Save box'), self.save_results_button] )


        # Widgets to select and delete fits
        self.selected_fit_index = None

        self.selection_dropdown = widgets.Dropdown(
            options=[('---', None),],
            value=None,
            description='Select fit:',
        )
        self.selection_dropdown.observe(self.__select_fit, 'value')

        self.delete_button = widgets.Button(description='Delete selected fit', disabled=True)
        self.delete_button.on_click(self.__delete_fit)

        self.delete_box = widgets.VBox(
            [
                widgets.Label('Delete box'),
                self.selection_dropdown,
                self.delete_button
            ]
        )



        # Auto search
        # Widgets to locate peaks using the scipy find_peaks method
        # and then automatically move between them performing a fit process
        # at each determined peak

        # Variable to hold the peaks line object for plotting
        self.peaks_line, = self.ax.plot([], 'xr')

        # Trigger to search for peaks
        self.find_peaks_button = widgets.Button(description='Find peaks')
        self.find_peaks_button.on_click(self.__peak_search)

        self.reset_peaks_button = widgets.Button(description='Clear peaks')
        self.reset_peaks_button.on_click(self.__clear_peaks)

        # FloatText widgets for parameter input for peak search
        self.auto_search_param_1 =  widgets.FloatText(
                                        value=1,
                                        description='height',
                                        continuous_update=False,
                                        disabled=False
                                    )
        self.auto_search_param_2 =  widgets.FloatText(
                                        value=0,
                                        description='threshold',
                                        continuous_update=False,
                                        disabled=False
                                    )
        self.auto_search_param_3 =  widgets.FloatText(
                                        value=20,
                                        description='distance',
                                        continuous_update=False,
                                        disabled=False
                                    )
        self.auto_search_param_4 =  widgets.FloatText(
                                        value=0.05,
                                        description='prominence',
                                        continuous_update=False,
                                        disabled=False
                                    )

        # Observe the search parameter boxes and update accordingly
        self.auto_search_param_1.observe(self.__update_peaksearch_param, 'value')
        self.auto_search_param_2.observe(self.__update_peaksearch_param, 'value')
        self.auto_search_param_3.observe(self.__update_peaksearch_param, 'value')
        self.auto_search_param_4.observe(self.__update_peaksearch_param, 'value')

        # Form the peak search widgets into a box
        self.auto_search_params_box = widgets.VBox(
            [
                widgets.Label('Auto peak search'),

                widgets.HBox(
                    [
                        self.find_peaks_button,
                        self.reset_peaks_button
                    ]
                ),
                self.auto_search_param_1,
                self.auto_search_param_2,
                self.auto_search_param_3,
                self.auto_search_param_4
            ]
        )

        # Widget to launch and cancel the automatic peak search fit process
        self.auto_start_button = widgets.Button(description='Start auto mode', disabled=True)
        self.auto_start_button.on_click(self.__enter_auto_mode)

        self.auto_exit_button = widgets.Button(description='Exit auto mode', disabled=True)
        self.auto_exit_button.on_click(self.__exit_auto_mode)


        # Controls during auto fit procedure
        self.auto_accept_peak_button = widgets.Button(description='Accept and continue', disabled=True)
        self.auto_accept_peak_button.on_click(self.__auto_accept)

        self.auto_reject_peak_button = widgets.Button(description='Reject', disabled=True)
        self.auto_reject_peak_button.on_click(self.__auto_reject)

        self.auto_retry_fit_button = widgets.Button(description='Redo fit', disabled=True)
        self.auto_retry_fit_button.on_click(self.__auto_refit)



        self.auto_enter_window_width = widgets.FloatText(
                                           value=1,
                                           description='Fit width (dx)',
                                           continuous_update=False,
                                           disabled=False
                                       )

        self.auto_enter_window_width_accept = widgets.Button(description='Rescale window', disabled=True)
        self.auto_enter_window_width_accept.on_click(self.__rescale_window)


        self.auto_out_on_fit =  widgets.IntText(
                                    value=0,
                                    description='On fit:',
                                    continuous_update=False,
                                    disabled=True
                                )

        self.auto_out_of_fit =  widgets.IntText(
                                    value=0,
                                    description='Out of total:',
                                    continuous_update=False,
                                    disabled=True
                                )




        self.auto_search_controls_box = widgets.VBox(
            [
                widgets.Label('Controls'),
                widgets.HBox(
                    [
                        self.auto_accept_peak_button,
                        self.auto_reject_peak_button,
                        self.auto_retry_fit_button
                    ]
                ),
                widgets.HBox(
                    [
                        self.auto_enter_window_width,
                        self.auto_enter_window_width_accept
                    ]
                ),
                widgets.HBox(
                    [
                        self.auto_out_on_fit,
                        self.auto_out_of_fit
                    ]
                ),
                widgets.Label('Turn on/off auto search mode:'),
                widgets.HBox(
                    [
                        self.auto_start_button,
                        self.auto_exit_button
                    ]
                )
            ]
        )



        self.auto_search_box = widgets.HBox(
            [
                self.auto_search_params_box,
                self.auto_search_controls_box
            ]
        )



        # Set the frontend
        box_layout = widgets.Layout(
                border='solid 1px black',
                margin='0px 10px 10px 0px',
                padding='5px 5px 5px 5px')

        self.ctrl_box.layout = box_layout
        self.save_box.layout = box_layout
        self.delete_box.layout = box_layout
        self.fit_box.layout = box_layout
        self.output.layout = box_layout
        self.output_box.layout = box_layout
        self.auto_search_params_box.layout = box_layout
        self.auto_search_box.layout = box_layout

        self.gui = widgets.VBox(
            [
                widgets.HBox(
                    [
                        self.ctrl_box,
                        self.save_box,
                        self.delete_box
                    ]
                ),

                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                self.fit_box,
                                self.output_box
                            ]
                        ),
                        self.output
                    ]
                ),

                self.auto_search_box

            ]
        )

        # Display the frontend
        display(self.gui)



    def __goto_FitMode(self, change):

        self.ctrl_b1.disabled=True
        self.ctrl_b2.disabled=False

        self.fitmodel_dropdown.disabled = False
        for param in self.param_box.children:
            param.disabled = False

        # Set the selected value to 0 and disable the selection box
        self.selection_dropdown.value = None
        self.selection_dropdown.disabled = True
        self.delete_button.disabled = True


        # Enable the fit buttons
        self.trigger_fit_button.disabled = False

        # Get the data in the domain of the fit range
        self.backend.fit_x, self.backend.fit_y = self.backend.get_data_in_range(self.ax.get_xlim())

        # Update the plot
        self.line.set_alpha(0.1)
        self.fit_region_data_line, = self.ax.plot(self.backend.fit_x, self.backend.fit_y, 'ko')

        # Make new current_fit_line
        self.current_fit_line, = plt.plot([])

        # Remove the accepted fit lines
        for line in self.fit_curve_lines:
            line.remove()


    def __goto_SearchMode(self, change):

        self.ctrl_b1.disabled=False
        self.ctrl_b2.disabled=True

        self.fitmodel_dropdown.disabled = True
        for param in self.param_box.children:
            param.disabled = True

        # Disable the fit buttons
        self.trigger_fit_button.disabled = True
        self.accept_fit_button.disabled = True

        # Enable the selection box
        self.selection_dropdown.disabled = False

        self.line.set_alpha(1)
        self.fit_region_data_line.remove()

        # Remove the current fit line
        self.current_fit_line.remove()


        # Add back the accepted fit lines
        for line in self.fit_curve_lines:
            self.ax.add_line(line)


    def __init_FitModel(self, change):

        # Get the correct model
        for model in self.backend.fit_models:
            if model.name == change.new:
                self.backend.cur_fitmodel = model
                break

        else:
            self.backend.cur_fitmodel = None

        if self.backend.cur_fitmodel is not None:

            # For each parameter, generate an input floattext widget
            # Create an observer and write the parameter values to the backend
            self.param_input_widgets = []
            self.param_output_widgets = []
            self.backend.param_vect = []

            for k in range(self.backend.cur_fitmodel.num_params):

                # Create the new input text widgets
                self.param_input_widgets.append(
                    widgets.FloatText(value=self.backend.cur_fitmodel.param_default[k],
                                      description=self.backend.cur_fitmodel.param_names[k],
                                      continuous_update=False,
                                      disabled=False
                                     )
                )

                # Create the new output text widgets
                self.param_output_widgets.append(
                widgets.FloatText(value=None,
                                  description=self.backend.cur_fitmodel.param_names[k],
                                  continuous_update=False,
                                  disabled=True
                                 )
                )

                # Construct the parameter backend values
                self.backend.param_vect.append(self.backend.cur_fitmodel.param_default[k])

                # Observe the input widgets
                self.param_input_widgets[k].observe(self.backend.update_param, 'value')


        # Update the widget container to include updated list
        self.param_box.children = self.param_input_widgets
        self.output_box.children = [self.trigger_fit_button, self.accept_fit_button] + self.param_output_widgets


    def update_results(self):
        # Method to update the fit line of the data

        # Update the output results widgets
        for output_widget, output in zip(self.param_output_widgets, self.backend.fit_params):
            output_widget.value = output

        # Plot the fit line
        self.current_fit_line.remove()
        self.current_fit_line, = self.ax.plot(self.backend.fit_x, self.backend.fit_result, 'C0', linewidth=2)

        # Enable the accept fit button
        self.accept_fit_button.disabled = False



    def __accept_fit(self, change):

        # Append the fitclass
        self.backend.fits.append(
            self.backend.fit_class(
                x = self.backend.fit_x,
                y = self.backend.fit_y,
                fit_model = self.backend.cur_fitmodel,
                fit_y = self.backend.fit_result,
                fit_params = self.backend.fit_params,
                fit_covmat = self.backend.fit_covmat,
                meta=self.backend.meta
            )
        )

        self.fit_curve_lines.append(
            self.current_fit_line
        )


        # Once the fit is accepted, refresh the fit list for selection
        self.selection_dropdown.options = [('---', None),] + [('Fit ' + str(i), i) for i in range(len(self.backend.fits))]


        self.__goto_SearchMode(change)



    def __select_fit(self, change):

        # Reset all fits to old color
        for line in self.fit_curve_lines:
            line.set_color('C0')

        if change.new is not None:
            # Enable the delete button
            self.delete_button.disabled = False

            # Change the color of the selected line
            #print('New curve selected at ' + str(change.new))
            self.fit_curve_lines[change.new].set_color('C1')

        # Disable the delete button when no fit is selected
        if change.new is None:
            self.delete_button.disabled = True

        # Record the selected fit
        self.selected_fit_index = change.new





    def __delete_fit(self, change):

        # Delete the fit in the backend
        self.backend.delete_fit(self.selected_fit_index)

        # Remove the line from the gui list
        line_to_remove = self.fit_curve_lines.pop(self.selected_fit_index)

        # Delete the line from the gui itself
        line_to_remove.remove()

        print('Successfuly removed line')

        # Reset the selection tool
        # Remove the option from the selection menu
        self.selection_dropdown.value = None
        self.selection_dropdown.options = [('---', None),] + [('Fit ' + str(i), i) for i in range(len(self.backend.fits))]
        self.selected_fit_index = None



    def __peak_search(self, change):

        # Look for peaks in the backend and check if any were found
        # If at least one peak is found then update the plot and enable the
        # various widgets.
        if self.backend.find_peaks():


            # Disable the start finding peaks button
            self.auto_start_button.disabled = False

            # Write the peaks
            self.peaks_line.set_data(self.backend.x[self.backend.peak_idxs],
                                     self.backend.y[self.backend.peak_idxs]
                                    )

            # Enable clear peaks
            self.reset_peaks_button.disabled = False

        else:
            print('No peaks found :( ')
            self.auto_start_button.disabled = True

        self.auto_out_of_fit.value = len(self.backend.peak_idxs)


    def __clear_peaks(self, change):
        # Remove the peaks from the plot
        self.peaks_line.set_data([],[])

        # Clear the backend
        self.backend.peak_idxs = []

        # Turn off the auto peak fit start button
        self.auto_start_button.disabled = True

        # Disable itself
        self.reset_peaks_button.disabled = True



    def __update_peaksearch_param(self, change):
        self.backend.peak_search_params_dict[change.owner.description] = change.new
        #print(self.backend.peak_search_params_dict)


    def __enter_auto_mode(self, change):

        # Enable the exit and accept/reject buttons
        # Disable the start and find_peaks buttons while running
        self.find_peaks_button.disabled = True
        self.auto_start_button.disabled = True
        self.auto_exit_button.disabled = False
        self.auto_accept_peak_button.disabled = False
        self.auto_reject_peak_button.disabled = False
        self.auto_retry_fit_button.disabled = False
        self.auto_enter_window_width_accept.disabled = False

        # Enable the fit module tools
        # Fit model dropdown selection, fit model parameters, etc.
        self.ctrl_b1.disabled=True # disable the fit data in range button

        self.fitmodel_dropdown.disabled = False
        for param in self.param_box.children:
            param.disabled = False

        # Set the selected value to 0 and disable the selection box
        self.selection_dropdown.value = None
        self.selection_dropdown.disabled = True
        self.delete_button.disabled = True


        # Update the plot
        self.line.set_alpha(0.1)

        # Make new current_fit_line
        self.current_fit_line, = plt.plot([])

        # Go to the first peak
        self.__goto_next_peak()



        # Wait for the accept/reject widgets to update the increment and move on.

    def __exit_auto_mode(self, change):

        # Enable the start button and find_peaks
        # Disable the other buttons
        self.find_peaks_button.disabled = False
        self.auto_start_button.disabled = False
        self.auto_exit_button.disabled = True
        self.auto_accept_peak_button.disabled = True
        self.auto_reject_peak_button.disabled = True
        self.auto_retry_fit_button.disabled = True
        self.auto_enter_window_width_accept.disabled = True


        # Disable the fit module tools
        # Fit model dropdown selection, fit model parameters, etc.
        self.ctrl_b1.disabled=False # disable the fit data in range button

        self.fitmodel_dropdown.disabled = True
        for param in self.param_box.children:
            param.disabled = True

        # Re-enable the dropdown Button
        self.selection_dropdown.disabled = False

        # Reset the current peak value to 0
        self.auto_out_on_fit.value = 0

        # Reset the main line color alpha
        self.line.set_alpha(1)

        # Clear out the fit data line
        try:
            self.fit_region_data_line.remove()
        except:
            pass

        # Remove the current fit line
        self.current_fit_line.remove()

        # Reset the x axis
        x_limits = (np.amin(self.backend.x), np.amax(self.backend.x))
        x_margin = (x_limits[1] - x_limits[0]) * 0.05  # 5% of window on each end
        self.ax.set_xlim(x_limits[0]-x_margin, x_limits[1]+x_margin)

        # Reset the y axis
        y_limits = (np.amin(self.backend.y), np.amax(self.backend.y))
        y_margin = (y_limits[1] - y_limits[0]) * 0.05  # 5% of window on each end
        self.ax.set_ylim(y_limits[0]-y_margin, y_limits[1]+y_margin)

        # Add back the accepted fit lines
        for line in self.fit_curve_lines:
            self.ax.add_line(line)


    def __goto_next_peak(self):

        # If already on the last fit, exit the auto fit mode
        if self.auto_out_on_fit.value == self.auto_out_of_fit.value:
            self.__exit_auto_mode(None)
            print('Finished!')

        else:
            # Increment the current peak counter
            self.auto_out_on_fit.value = self.auto_out_on_fit.value + 1

            # Get the idx of the peak being looked at
            self.cur_peak_idx = self.backend.peak_idxs[self.auto_out_on_fit.value-1]

            # Set the window
            self.__rescale_window(None) # This method also updates the fit data in the backend

            # Update the parameter for the peak position
            # List of names is hard coded and prioritized in order of label
            for param_name in ['mu', 'mu0', 'mu1', 'x0']:
                try:
                    position_param_index = self.backend.cur_fitmodel.param_names.index(param_name)
                    self.param_box.children[position_param_index].value = self.backend.x[self.cur_peak_idx]
                    break
                except:
                    pass


            # Run a fit onthe window
            self.__auto_refit(None)


    def __auto_accept(self, change):

        # Append the fitclass
        self.backend.fits.append(
            self.backend.fit_class(
                x = self.backend.fit_x,
                y = self.backend.fit_y,
                fit_model = self.backend.cur_fitmodel,
                fit_y = self.backend.fit_result,
                fit_params = self.backend.fit_params,
                fit_covmat = self.backend.fit_covmat,
                meta=self.backend.meta
            )
        )

        self.fit_curve_lines.append(
            self.current_fit_line
        )


        # Once the fit is accepted, refresh the fit list for selection
        self.selection_dropdown.options = [('---', None),] + [('Fit ' + str(i), i) for i in range(len(self.backend.fits))]


        self.__goto_next_peak()



    def __auto_reject(self, change):
        self.__goto_next_peak()



    def __auto_refit(self, change):

        self.backend.fit_data(None)
        self.accept_fit_button.disabled = True



    def __rescale_window(self, change):

        # Get the window width
        self.data_range = (
            self.backend.x[self.cur_peak_idx] - self.auto_enter_window_width.value/2,
            self.backend.x[self.cur_peak_idx] + self.auto_enter_window_width.value/2
        )

        # Change the fit data to whatever is in the range
        self.backend.fit_x, self.backend.fit_y = self.backend.get_data_in_range(
            self.data_range
        )

        # Reset the data line
        try:
            self.fit_region_data_line.remove()
        except:
            pass
        self.fit_region_data_line, = self.ax.plot(self.backend.fit_x, self.backend.fit_y, 'ko')


        # Set the x axis
        x_margin = self.auto_enter_window_width.value * 0.05  # 5% of window on each end
        self.ax.set_xlim(self.data_range[0] - x_margin, self.data_range[1] + x_margin)

        # Set the y axis
        y_limits = (np.amin(self.backend.fit_y), np.amax(self.backend.fit_y))
        y_margin = (y_limits[1] - y_limits[0]) * 0.05  # 5% of window on each end
        self.ax.set_ylim(y_limits[0]-y_margin, y_limits[1]+y_margin)