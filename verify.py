from read_var import read_init_vars_json

variables = read_init_vars_json('./results/galilei/3/partial_solution_9.json')
x_values = variables['x']
y_values = variables['y']
u_values = variables['u']
z_max_values = variables['z_max']